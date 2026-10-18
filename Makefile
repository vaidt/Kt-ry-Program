.PHONY: help doctor bootstrap validate-delegations compile test test-runtime build ci-local clean

PYTHON ?= .venv/bin/python

help:
	@echo "ASIG workspace commands:"
	@echo "  make bootstrap             Create .venv and install local package/build tooling"
	@echo "  make doctor                Display available Python/Node/Rust/Git versions"
	@echo "  make validate-delegations  Validate delegation records fail-closed"
	@echo "  make compile               Compile source, scripts, and tests"
	@echo "  make test                  Run all unit and contract tests"
	@echo "  make test-runtime          Run Python/Node/Rust adapter tests"
	@echo "  make build                 Build wheel and source distribution with checksums"
	@echo "  make ci-local              Run the local pre-PR validation sequence"
	@echo "  make clean                 Remove local build outputs"

bootstrap:
	python -m venv .venv
	.venv/bin/python -m pip install --disable-pip-version-check --upgrade pip build
	.venv/bin/python -m pip install --disable-pip-version-check -e .

doctor:
	@python --version
	@node --version
	@rustc --version
	@cargo --version
	@git --version
	@$(PYTHON) -m pip --version

validate-delegations:
	$(PYTHON) scripts/validate_project_delegations.py --records-dir governance/delegations/records --schema schemas/project-delegation.schema.json --report .artifacts/project-delegation-validation.json

compile:
	$(PYTHON) -m compileall -q src scripts tests

test:
	$(PYTHON) -m unittest discover -s tests -v

test-runtime:
	$(PYTHON) -m unittest discover -s tests -p "test_*runtime.py" -v

build:
	mkdir -p .artifacts
	$(PYTHON) -m build --outdir .artifacts/dist
	cd .artifacts/dist && sha256sum *.whl *.tar.gz > SHA256SUMS.txt

ci-local: validate-delegations compile test test-runtime build

clean:
	rm -rf build dist .artifacts .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
