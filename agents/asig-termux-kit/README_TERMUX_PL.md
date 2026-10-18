# ASIG Artifact Archiver — Termux / Android

Pakiet zawiera dwa skrypty Bash:

- `archive_asig_termux.sh` — pobiera oryginalny ZIP z GitHub Actions, sprawdza przypięty digest SHA-256, tworzy kopię rozpakowanej zawartości do łatwego przeglądu, zapisuje metadane i sumy plików.
- `verify_asig_archive.sh` — ponownie sprawdza sumy plików, digest oryginalnego ZIP-a, poprawność ZIP-a oraz asercje zapisane w raportach workflow; jeśli zainstalowane są `cosign` i/lub `gh`, uruchamia też niezależne kontrole kryptograficzne.

## 1. Instalacja w Termux

Otwórz Termux i wykonaj:

```bash
pkg update
pkg upgrade
pkg install bash curl jq coreutils findutils grep sed git openssh unzip
```

`cosign` i `gh` są opcjonalne dla samego pobrania i kontroli SHA-256. Bez nich skrypt oznaczy odpowiednią niezależną weryfikację jako `NOT_RUN` — nie jako sukces. Dostępność i możliwość uruchomienia binariów Cosign na Androidzie zależą od architektury/środowiska. Cosign należy instalować z zaufanego źródła i zweryfikować przed użyciem.

## 2. Rozpakowanie pakietu

Po pobraniu pliku `asig-termux-kit.zip` do katalogu `Download` w Termux możesz użyć:

```bash
termux-setup-storage
mkdir -p ~/asig-termux
unzip /sdcard/Download/asig-termux-kit.zip -d ~/asig-termux
cd ~/asig-termux/asig-termux-kit
chmod 700 *.sh
```

Jeśli pliki znajdują się już w innym katalogu, przejdź bezpośrednio do tego katalogu.

## 3. Pobranie i archiwizacja lokalna

Uruchom:

```bash
./archive_asig_termux.sh
```

Gdy skrypt poprosi o token, wklej token GitHub z uprawnieniem **Actions: Read** do repozytorium `vaidt/Kt-ry-Program`. Wejście tokena nie jest wyświetlane. Nie zapisuj tokena wewnątrz skryptu ani w repozytorium. Możesz także wcześniej ustawić `GH_TOKEN` w swojej sesji.

Domyślne wartości są celowo przypięte do artefaktu znanego z rozmowy:

- repozytorium: `vaidt/Kt-ry-Program`
- run: `39161809100`
- artifact ID: `12149187209`
- commit: `519ad82c2872e20f7b45bdc5dd332c0c572e627a`
- oczekiwany SHA-256 ZIP-a: `2f25e79c1ff59706ab2309451fb84de7d286c4bf53057010be885d65920764fd`

Skrypt przerwie pobieranie, jeśli digest GitHub albo commit nie zgadza się z powyższą wartością. Nie nadpisuje istniejącego katalogu. Aby użyć innego miejsca wyjściowego:

```bash
OUTPUT_DIR="$HOME/storage/shared/ASIG-archive-39161809100" ./archive_asig_termux.sh
```

## 4. Ponowna kontrola archiwum

Podaj katalog utworzony przez skrypt:

```bash
./verify_asig_archive.sh "$HOME/asig-termux/asig-termux-kit/asig-evidence-archive-39161809100"
```

Dostosuj ścieżkę do rzeczywistego katalogu podanego na końcu działania skryptu.

## 5. Opcjonalny push do zewnętrznego repozytorium dowodowego

Nie ustawiono fikcyjnego repozytorium domyślnego. Najpierw utwórz lub wskaż prawdziwe repozytorium docelowe. Push wymaga uwierzytelnienia Git (SSH lub skonfigurowany credential helper) oraz tego, by **obie niezależne kontrole** zakończyły się `PASS`: Cosign i GitHub Attestation.

Przykład przez SSH — zastąp poniższy adres własnym, istniejącym repozytorium:

```bash
EVIDENCE_REPO='git@github.com:OWNER/REPO-DOWODOWE.git' \
EVIDENCE_BRANCH='main' \
./archive_asig_termux.sh --push
```

Nie uruchamiaj przykładu bez zastąpienia `OWNER/REPO-DOWODOWE` poprawnym repozytorium. Skrypt nie nadpisze istniejącego katalogu runu w repozytorium dowodowym. Nie wkładaj tokena do URL-a Git.

## Co jest sprawdzane

1. Digest zwrócony przez GitHub API jest zgodny z wcześniej przypiętym SHA-256.
2. Pobrany oryginalny ZIP ma ten sam SHA-256 i przechodzi `unzip -t`.
3. Oryginalny ZIP jest zachowany bez modyfikacji w `original_zips/`.
4. `payload/` to tylko kopia rozpakowana dla wygody — nie zastępuje oryginalnego ZIP-a.
5. `sha256sums.txt` obejmuje wszystkie pliki archiwum poza samym `sha256sums.txt`.
6. Raporty `EXACT_MATCH` są traktowane jako raporty utworzone przez workflow. Nie są mylone z niezależną lokalną weryfikacją.
7. `cosign verify-blob` używa bundle, manifestu, dokładnej tożsamości workflow `manifest-sign-verify.yml@refs/heads/main` i wystawcy `https://token.actions.githubusercontent.com`.
8. Jeśli `gh` jest dostępne, `gh attestation verify` sprawdza atestację GitHub dla manifestu i oczekiwanego workflow.

## Ograniczenia i bezpieczeństwo

- Archiwizacja lokalna nie oznacza jeszcze wysłania danych do repozytorium dowodowego.
- Jeżeli Cosign/gh nie są dostępne, wynik to `NOT_RUN`, a nie `PASS`.
- Domyślne wartości są przypięte do jednego, konkretnego artefaktu. Dla innego runu trzeba świadomie zaktualizować zmienne oraz oczekiwany digest.
- Artefakt GitHub Actions miał wyznaczone wygaśnięcie `2026-11-01T20:07:14Z`. Lokalną kopię należy dodatkowo skopiować na trwały nośnik.
