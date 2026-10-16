PYTHON ?= python3

.PHONY: validate test

validate:
	PYTHONPATH=src $(PYTHON) scripts/validate_catalog.py
	$(PYTHON) -m compileall -q src scripts tests

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
