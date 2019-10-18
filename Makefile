.DEFAULT_GOAL := test
black = black -S -l 120 --target-version py37
isort = isort -rc

.PHONY: reset-db
reset-db:
	psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS stockwatch"
	psql -h localhost -U postgres -c "CREATE DATABASE stockwatch"

.PHONY: test
test:
	pytest StockWatch/ --cov=StockWatch

.PHONY: lint
lint:
	flake8 StockWatch
	$(isort) --check-only StockWatch
	$(black) --check StockWatch

.PHONY: format
format:
	$(isort) StockWatch
	$(black) StockWatch

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -r requirements.txt

.PHONY: install-all
install-all: install
	grablib
