PY = python
PIP = pip

.PHONY: deps deps-dev test lint fmt type run

deps:
	$(PIP) install -r requirements.txt

deps-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install

lint:
	ruff check .
fmt:
	ruff format .
	black src tests

type:
	mypy src

test:
	pytest -q --cov=src --cov-report=term-missing

run:
	$(PY) src/main.py
