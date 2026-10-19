#!/data/data/com.termux/files/usr/bin/bash
# Offline checks for an ASIG evidence archive directory created by archive_asig_termux.sh.
set -Eeuo pipefail
umask 077

REPO="${REPO:-vaidt/Kt-ry-Program}"
EXPECTED_ARTIFACT_SHA256="${EXPECTED_ARTIFACT_SHA256:-2f25e79c1ff59706ab2309451fb84de7d286c4bf53057010be885d65920764fd}"
COSIGN_IDENTITY="https://github.com/${REPO}/.github/workflows/manifest-sign-verify.yml@refs/heads/main"
COSIGN_ISSUER="https://token.actions.githubusercontent.com"

fail() { printf 'BŁĄD: %s\n' "$*" >&2; exit 1; }
[[ $# -eq 1 ]] || fail "Użycie: ./verify_asig_archive.sh /ścieżka/do/asig-evidence-archive-RUN_ID"
DIR="${1%/}"
[[ -d "$DIR" ]] || fail "Nie ma katalogu: $DIR"
for cmd in jq sha256sum unzip find; do command -v "$cmd" >/dev/null 2>&1 || fail "Brak polecenia: $cmd"; done
[[ -s "$DIR/manifest.json" ]] || fail "Brak manifest.json."
[[ -s "$DIR/sha256sums.txt" ]] || fail "Brak sha256sums.txt."
if grep -q 'sha256sums.txt' "$DIR/sha256sums.txt"; then fail "sha256sums.txt nie może zawierać własnej sumy."; fi

printf '1/4 Sprawdzam sumy plików...\n'
(cd "$DIR" && sha256sum -c sha256sums.txt)

printf '2/4 Sprawdzam metadane i oryginalny ZIP...\n'
FORMAT="$(jq -r '.format // empty' "$DIR/manifest.json")"
[[ "$FORMAT" == "ASIG-TERMUX-EVIDENCE-ARCHIVE" ]] || fail "Nieznany format manifestu."
ZIP_REL="$(jq -r '.artifact.original_zip_path // empty' "$DIR/manifest.json")"
ZIP_SHA="$(jq -r '.artifact.downloaded_zip_sha256 // empty' "$DIR/manifest.json")"
[[ -n "$ZIP_REL" && -s "$DIR/$ZIP_REL" ]] || fail "Brak ZIP-a wskazanego w manifest.json."
[[ "$ZIP_SHA" == "$EXPECTED_ARTIFACT_SHA256" ]] || fail "Manifest ZIP SHA-256 różni się od oczekiwanej przypiętej sumy."
COMPUTED="$(sha256sum "$DIR/$ZIP_REL" | awk '{print $1}')"
[[ "$COMPUTED" == "$EXPECTED_ARTIFACT_SHA256" ]] || fail "SHA-256 ZIP-a jest niezgodne."
unzip -tq "$DIR/$ZIP_REL" >/dev/null || fail "ZIP jest uszkodzony."

printf '3/4 Sprawdzam raporty workflow...\n'
for r in "$DIR/payload/cosign-verification.json" "$DIR/payload/github-attestation-verification.json"; do
  [[ -s "$r" ]] || fail "Brak raportu: $r"
  jq -e '.status == "EXACT_MATCH" and .signature_status == "valid" and .signature_valid == true and .errors == []' "$r" >/dev/null \
    || fail "Raport workflow nie spełnia asercji oczekiwanych: $r"
done

printf '4/4 Opcjonalna niezależna weryfikacja kryptograficzna...\n'
MANIFEST="$DIR/payload/asig-manifest.json"
BUNDLE="$DIR/payload/asig-manifest.sigstore.json"
if command -v cosign >/dev/null 2>&1; then
  cosign verify-blob "$MANIFEST" --bundle "$BUNDLE" \
    --certificate-identity "$COSIGN_IDENTITY" \
    --certificate-oidc-issuer "$COSIGN_ISSUER"
  echo "Cosign: PASS"
else
  echo "Cosign: NOT RUN (narzędzie nie jest zainstalowane; to nie jest PASS)."
fi
if command -v gh >/dev/null 2>&1; then
  if [[ -n "${GH_TOKEN:-${GITHUB_TOKEN:-}}" ]]; then
    GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}" gh attestation verify "$MANIFEST" --repo "$REPO" \
      --signer-workflow "$REPO/.github/workflows/manifest-sign-verify.yml"
    echo "GitHub Attestation: PASS"
  else
    echo "GitHub Attestation: NOT RUN (ustaw GH_TOKEN/GITHUB_TOKEN albo pomiń)."
  fi
else
  echo "GitHub Attestation: NOT RUN (gh nie jest zainstalowany; to nie jest PASS)."
fi

echo "OK: integralność lokalnego archiwum i zapisane raporty przeszły kontrole."
echo "Uwaga: niezależna kontrola Cosign/Attestation została wykonana tylko, jeśli odpowiednie narzędzia są dostępne i polecenia zakończyły się kodem 0."
