#!/data/data/com.termux/files/usr/bin/bash
# ASIG artifact archiver for Termux / Android.
# Downloads the original GitHub Actions ZIP, checks its pinned digest,
# preserves the ZIP and payload, and creates a SHA-256 inventory.
set -Eeuo pipefail
umask 077

REPO="${REPO:-vaidt/Kt-ry-Program}"
RUN_ID="${RUN_ID:-39161809100}"
ARTIFACT_ID="${ARTIFACT_ID:-12149187209}"
EXPECTED_ARTIFACT_SHA256="${EXPECTED_ARTIFACT_SHA256:-2f25e79c1ff59706ab2309451fb84de7d286c4bf53057010be885d65920764fd}"
EXPECTED_HEAD_SHA="${EXPECTED_HEAD_SHA:-519ad82c2872e20f7b45bdc5dd332c0c572e627a}"
EXPECTED_ARTIFACT_NAME="${EXPECTED_ARTIFACT_NAME:-asig-signed-manifest-519ad82c2872e20f7b45bdc5dd332c0c572e627a}"
OUTPUT_DIR="${OUTPUT_DIR:-$PWD/asig-evidence-archive-${RUN_ID}}"
EVIDENCE_REPO="${EVIDENCE_REPO:-}"
EVIDENCE_BRANCH="${EVIDENCE_BRANCH:-main}"
COSIGN_IDENTITY="https://github.com/${REPO}/.github/workflows/manifest-sign-verify.yml@refs/heads/main"
COSIGN_ISSUER="https://token.actions.githubusercontent.com"
API_BASE="https://api.github.com"
PUSH=0

usage() {
  cat <<'USAGE'
Użycie:
  ./archive_asig_termux.sh [--push]

Domyślnie tworzy lokalne archiwum. --push dodatkowo wysyła je do repozytorium
wskazanego przez EVIDENCE_REPO, ale tylko gdy lokalna weryfikacja Cosign
oraz GitHub Attestation zakończą się powodzeniem.

Opcjonalne zmienne: REPO, RUN_ID, ARTIFACT_ID, OUTPUT_DIR,
EXPECTED_ARTIFACT_SHA256, EXPECTED_HEAD_SHA, EVIDENCE_REPO, EVIDENCE_BRANCH.
USAGE
}

fail() { printf 'BŁĄD: %s\n' "$*" >&2; exit 1; }
info() { printf '\n==> %s\n' "$*"; }

while (($#)); do
  case "$1" in
    --push) PUSH=1 ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Nieznany argument: $1 (użyj --help)." ;;
  esac
  shift
done

for cmd in curl jq sha256sum unzip find sort awk sed grep date mktemp; do
  command -v "$cmd" >/dev/null 2>&1 || fail "Brak polecenia '$cmd'. Zainstaluj je przez pkg install." 
done

TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  printf 'Wklej token GitHub z uprawnieniem Actions: Read (nie będzie zapisany na dysku): '
  IFS= read -r -s TOKEN
  printf '\n'
fi
[[ -n "$TOKEN" ]] || fail "Nie podano tokena GitHub."

# Normalize the output path and refuse to overwrite a prior evidence record.
OUT_PARENT="$(dirname "$OUTPUT_DIR")"
OUT_BASE="$(basename "$OUTPUT_DIR")"
mkdir -p "$OUT_PARENT"
OUT_PARENT="$(cd "$OUT_PARENT" && pwd)"
OUT_DIR="${OUT_PARENT}/${OUT_BASE}"
[[ ! -e "$OUT_DIR" ]] || fail "Katalog już istnieje: $OUT_DIR. Podaj nowy OUTPUT_DIR; nie nadpisuję dowodów."
mkdir -p "$OUT_DIR/original_zips" "$OUT_DIR/payload" "$OUT_DIR/cosign-reports" "$OUT_DIR/attestation-reports"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
API_URL="${API_BASE}/repos/${REPO}/actions/runs/${RUN_ID}/artifacts?per_page=100"

info "Pobieram metadane artefaktu z GitHub API"
HTTP_BODY="$TMP_DIR/artifacts.json"
HTTP_CODE="$(curl --silent --show-error --output "$HTTP_BODY" --write-out '%{http_code}' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2022-11-28' \
  "$API_URL")" || fail "Błąd połączenia z GitHub API."
[[ "$HTTP_CODE" == "200" ]] || fail "GitHub API zwróciło HTTP $HTTP_CODE: $(jq -r '.message // "brak szczegółów"' "$HTTP_BODY" 2>/dev/null || true)"
ARTIFACT_JSON="$(jq -ce --argjson id "$ARTIFACT_ID" '.artifacts[] | select(.id == $id)' "$HTTP_BODY")" \
  || fail "Artefakt ID $ARTIFACT_ID nie występuje w runie $RUN_ID."
printf '%s\n' "$ARTIFACT_JSON" > "$OUT_DIR/artifacts_api.json"

ACTUAL_ID="$(jq -r '.id' <<<"$ARTIFACT_JSON")"
ACTUAL_NAME="$(jq -r '.name' <<<"$ARTIFACT_JSON")"
ACTUAL_DIGEST="$(jq -r '.digest // empty' <<<"$ARTIFACT_JSON" | sed 's/^sha256://')"
ACTUAL_RUN="$(jq -r '.workflow_run.id // empty' <<<"$ARTIFACT_JSON")"
ACTUAL_HEAD="$(jq -r '.workflow_run.head_sha // empty' <<<"$ARTIFACT_JSON")"
EXPIRED="$(jq -r '.expired' <<<"$ARTIFACT_JSON")"
[[ "$ACTUAL_ID" == "$ARTIFACT_ID" ]] || fail "ID artefaktu nie pasuje."
[[ "$ACTUAL_RUN" == "$RUN_ID" ]] || fail "Artefakt przypisany do innego runu: $ACTUAL_RUN."
[[ "$ACTUAL_NAME" == "$EXPECTED_ARTIFACT_NAME" ]] || fail "Nieoczekiwana nazwa artefaktu: $ACTUAL_NAME."
[[ "$ACTUAL_HEAD" == "$EXPECTED_HEAD_SHA" ]] || fail "Nieoczekiwany commit źródłowy: $ACTUAL_HEAD."
[[ "$ACTUAL_DIGEST" == "$EXPECTED_ARTIFACT_SHA256" ]] || fail "Digest GitHub ($ACTUAL_DIGEST) różni się od przypiętej wartości ($EXPECTED_ARTIFACT_SHA256)."
[[ "$EXPIRED" == "false" ]] || fail "Artefakt jest oznaczony jako wygasły."

ZIP_NAME="${ACTUAL_NAME}-${ACTUAL_ID}.zip"
ZIP_PATH="$OUT_DIR/original_zips/$ZIP_NAME"
DOWNLOAD_URL="${API_BASE}/repos/${REPO}/actions/artifacts/${ARTIFACT_ID}/zip"
HEADERS="$TMP_DIR/download-headers.txt"

info "Pobieram oryginalny ZIP (bez przepakowywania)"
DL_CODE="$(curl --silent --show-error --dump-header "$HEADERS" --output /dev/null --write-out '%{http_code}' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Accept: application/vnd.github+json' \
  -H 'X-GitHub-Api-Version: 2022-11-28' \
  "$DOWNLOAD_URL")" || fail "Nie udało się uzyskać URL pobierania artefaktu."
[[ "$DL_CODE" == "302" ]] || fail "Endpoint pobierania zwrócił HTTP $DL_CODE (oczekiwano 302)."
LOCATION="$(awk 'tolower($1)=="location:" {sub(/^[^:]*:[[:space:]]*/, ""); sub(/\r$/, ""); value=$0} END{print value}' "$HEADERS")"
[[ "$LOCATION" == https://* ]] || fail "Brak poprawnego HTTPS Location w odpowiedzi GitHub."
# Do signed storage URL nie przekazujemy tokena GitHub.
curl --fail --silent --show-error --location --retry 3 --retry-delay 1 \
  --output "$ZIP_PATH" "$LOCATION" || fail "Pobranie ZIP-a nie powiodło się."

ACTUAL_ZIP_SHA="$(sha256sum "$ZIP_PATH" | awk '{print $1}')"
[[ "$ACTUAL_ZIP_SHA" == "$EXPECTED_ARTIFACT_SHA256" ]] || fail "SHA-256 pobranego ZIP-a ($ACTUAL_ZIP_SHA) nie zgadza się z digestem GitHub. ZIP pozostawiono w: $ZIP_PATH"
unzip -tq "$ZIP_PATH" >/dev/null || fail "Test integralności ZIP nie powiódł się."
# Reject archive entries that attempt absolute paths or parent-directory traversal.
if unzip -Z1 "$ZIP_PATH" | grep -Eq '(^/|(^|/)\.\.(/|$))'; then
  fail "ZIP zawiera niebezpieczne ścieżki; nie rozpakowuję zawartości."
fi
unzip -q "$ZIP_PATH" -d "$OUT_DIR/payload" || fail "Rozpakowanie kopii payload nie powiodło się. Oryginalny ZIP zachowano."

MANIFEST="$OUT_DIR/payload/asig-manifest.json"
COSIGN_BUNDLE="$OUT_DIR/payload/asig-manifest.sigstore.json"
COSIGN_REPORT="$OUT_DIR/payload/cosign-verification.json"
GH_REPORT="$OUT_DIR/payload/github-attestation-verification.json"
for f in "$MANIFEST" "$COSIGN_BUNDLE" "$COSIGN_REPORT" "$GH_REPORT"; do
  [[ -s "$f" ]] || fail "Brak wymaganego pliku wewnątrz artefaktu: $(basename "$f")."
done

info "Sprawdzam raporty wygenerowane przez workflow"
REPORTS_STATUS="PASS"
for f in "$COSIGN_REPORT" "$GH_REPORT"; do
  if ! jq -e '.status == "EXACT_MATCH" and .signature_status == "valid" and .signature_valid == true and .errors == []' "$f" >/dev/null; then
    REPORTS_STATUS="FAIL"
    printf 'BŁĄD: raport workflow nie ma oczekiwanego statusu: %s\n' "$f" >&2
  fi
done

COSIGN_STATUS="NOT_RUN_TOOL_UNAVAILABLE"
if command -v cosign >/dev/null 2>&1; then
  info "Niezależnie weryfikuję podpis blob przez Cosign"
  if cosign verify-blob "$MANIFEST" --bundle "$COSIGN_BUNDLE" \
      --certificate-identity "$COSIGN_IDENTITY" \
      --certificate-oidc-issuer "$COSIGN_ISSUER" \
      >"$OUT_DIR/cosign-reports/cosign-verify-blob.txt" 2>&1; then
    COSIGN_STATUS="PASS"
  else
    COSIGN_STATUS="FAIL"
    cat "$OUT_DIR/cosign-reports/cosign-verify-blob.txt" >&2
  fi
else
  printf '%s\n' "Cosign nie jest zainstalowany; podpis nie został niezależnie zweryfikowany." > "$OUT_DIR/cosign-reports/NOT_RUN.txt"
fi

GH_ATTESTATION_STATUS="NOT_RUN_TOOL_UNAVAILABLE"
if command -v gh >/dev/null 2>&1; then
  info "Niezależnie weryfikuję GitHub Attestation manifestu"
  if GH_TOKEN="$TOKEN" gh attestation verify "$MANIFEST" --repo "$REPO" \
      --signer-workflow "$REPO/.github/workflows/manifest-sign-verify.yml" \
      >"$OUT_DIR/attestation-reports/gh-attestation-verify.txt" 2>&1; then
    GH_ATTESTATION_STATUS="PASS"
  else
    GH_ATTESTATION_STATUS="FAIL"
    cat "$OUT_DIR/attestation-reports/gh-attestation-verify.txt" >&2
  fi
else
  printf '%s\n' "GitHub CLI (gh) nie jest zainstalowany; atestacja nie została niezależnie zweryfikowana." > "$OUT_DIR/attestation-reports/NOT_RUN.txt"
fi

DOWNLOADED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
jq -n \
  --arg repo "$REPO" --arg run_id "$RUN_ID" \
  --arg run_url "https://github.com/${REPO}/actions/runs/${RUN_ID}" \
  --arg downloaded_at "$DOWNLOADED_AT" --arg sha "$ACTUAL_ZIP_SHA" \
  --arg cosign "$COSIGN_STATUS" --arg gh_attestation "$GH_ATTESTATION_STATUS" \
  --arg reports "$REPORTS_STATUS" --arg identity "$COSIGN_IDENTITY" \
  --arg issuer "$COSIGN_ISSUER" --argjson artifact "$ARTIFACT_JSON" \
  '{format:"ASIG-TERMUX-EVIDENCE-ARCHIVE",version:1,repository:$repo,run:{id:$run_id,url:$run_url,head_sha:$artifact.workflow_run.head_sha,head_branch:$artifact.workflow_run.head_branch},downloaded_at_utc:$downloaded_at,artifact:{id:$artifact.id,name:$artifact.name,created_at:$artifact.created_at,expires_at:$artifact.expires_at,api_digest:$artifact.digest,downloaded_zip_sha256:$sha,size_in_bytes:$artifact.size_in_bytes,original_zip_path:("original_zips/" + $artifact.name + "-" + ($artifact.id|tostring) + ".zip")},verification:{workflow_reports:$reports,cosign_live_check:$cosign,github_attestation_live_check:$gh_attestation,cosign_certificate_identity:$identity,cosign_oidc_issuer:$issuer,note:"Embedded workflow reports are historical outputs. Live checks are separately marked and are not inferred from those reports."}}' \
  > "$OUT_DIR/manifest.json"

cat > "$OUT_DIR/README.txt" <<EOF2
ASIG evidence archive
Repository: $REPO
Run ID: $RUN_ID
Artifact ID: $ARTIFACT_ID
Pinned GitHub artifact SHA-256: $EXPECTED_ARTIFACT_SHA256
Downloaded ZIP SHA-256: $ACTUAL_ZIP_SHA
Downloaded at (UTC): $DOWNLOADED_AT

original_zips/ contains the original downloaded ZIP unchanged.
payload/ contains a convenience extraction of the ZIP; it is not a replacement for the original.
manifest.json records GitHub metadata and distinguishes workflow-generated reports from live verification.
sha256sums.txt covers every regular file in this archive except sha256sums.txt itself.

Do not treat workflow-generated reports alone as an independent local signature verification.
EOF2

# Snapshot file list and hash all files except the checksum file itself.
(
  cd "$OUT_DIR"
  find . -type f ! -name 'filelist.txt' ! -name 'sha256sums.txt' -print | LC_ALL=C sort > filelist.txt
  find . -type f ! -name 'sha256sums.txt' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > sha256sums.txt
)

info "Archiwum lokalne zostało utworzone"
printf 'Katalog: %s\n' "$OUT_DIR"
printf 'Oryginalny ZIP SHA-256: %s\n' "$ACTUAL_ZIP_SHA"
printf 'Raporty z workflow: %s\nCosign live: %s\nGitHub Attestation live: %s\n' "$REPORTS_STATUS" "$COSIGN_STATUS" "$GH_ATTESTATION_STATUS"

if ((PUSH)); then
  command -v git >/dev/null 2>&1 || fail "--push wymaga git (pkg install git). Archiwum lokalne: $OUT_DIR"
  [[ -n "$EVIDENCE_REPO" ]] || fail "--push wymaga EVIDENCE_REPO wskazującego rzeczywiste repo dowodowe. Archiwum lokalne: $OUT_DIR"
  [[ "$REPORTS_STATUS" == "PASS" ]] || fail "Odmowa push: raporty workflow nie przeszły kontroli. Archiwum lokalne: $OUT_DIR"
  [[ "$COSIGN_STATUS" == "PASS" ]] || fail "Odmowa push: niezależna weryfikacja Cosign nie zakończyła się PASS. Archiwum lokalne: $OUT_DIR"
  [[ "$GH_ATTESTATION_STATUS" == "PASS" ]] || fail "Odmowa push: niezależna weryfikacja GitHub Attestation nie zakończyła się PASS. Archiwum lokalne: $OUT_DIR"
  PUSH_TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR" "$PUSH_TMP"' EXIT
  info "Klonuję repozytorium dowodowe i wysyłam bez nadpisywania istniejącego wpisu"
  git clone --depth 1 --branch "$EVIDENCE_BRANCH" "$EVIDENCE_REPO" "$PUSH_TMP/repo"
  TARGET="$PUSH_TMP/repo/$RUN_ID"
  [[ ! -e "$TARGET" ]] || fail "W repo dowodowym istnieje już $RUN_ID. Nie nadpisuję. Archiwum lokalne: $OUT_DIR"
  mkdir -p "$TARGET"
  cp -R "$OUT_DIR/." "$TARGET/"
  git -C "$PUSH_TMP/repo" config user.name "${GIT_AUTHOR_NAME:-ASIG Termux Archiver}"
  git -C "$PUSH_TMP/repo" config user.email "${GIT_AUTHOR_EMAIL:-asig-archiver@localhost}"
  git -C "$PUSH_TMP/repo" add -- "$RUN_ID"
  git -C "$PUSH_TMP/repo" commit -m "Archive ASIG artifact for Actions run $RUN_ID"
  git -C "$PUSH_TMP/repo" push origin "$EVIDENCE_BRANCH"
  printf '\nWysłano archiwum do %s, branch %s, katalog %s.\n' "$EVIDENCE_REPO" "$EVIDENCE_BRANCH" "$RUN_ID"
fi

if [[ "$REPORTS_STATUS" != "PASS" ]]; then
  fail "Archiwum zachowano, ale raporty workflow nie przeszły kontroli. Nie wysłano zdalnie. Katalog: $OUT_DIR"
fi
if [[ "$COSIGN_STATUS" == "FAIL" || "$GH_ATTESTATION_STATUS" == "FAIL" ]]; then
  fail "Archiwum zachowano, lecz weryfikacja kryptograficzna zakończyła się błędem. Nie wysłano zdalnie. Katalog: $OUT_DIR"
fi
if [[ "$COSIGN_STATUS" != "PASS" || "$GH_ATTESTATION_STATUS" != "PASS" ]]; then
  printf '\nUWAGA: archiwizacja lokalna ukończona, ale nie wszystkie kontrole kryptograficzne uruchomiono. Nie traktuj archiwum jako w pełni niezależnie zweryfikowanego.\n'
fi
