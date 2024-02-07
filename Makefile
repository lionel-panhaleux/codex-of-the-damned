.PHONY: po-update po-compile po release test update

po-update:
	pybabel extract --charset=utf-8 -c "TRANSLATORS:" -w 120 -k lazy_gettext -F babel.cfg -o messages.pot codex_of_the_damned
	pybabel update -l fr -w 120 --init-missing -i messages.pot -d codex_of_the_damned/translations

po-compile:
	pybabel compile -D messages -d codex_of_the_damned/translations

po: po-update po-compile

release:
	fullrelease
	pip install -e ".[dev]"

test:
	black --check codex_of_the_damned tests
	ruff check
	pytest

update:
	pip install --upgrade --upgrade-strategy eager -e ".[dev]"
