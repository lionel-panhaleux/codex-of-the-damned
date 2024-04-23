.PHONY: po-update po-compile po check-porcelain clean release-local release test update

BABEL_LANG ?= fr
NEXT_VERSION = `python -m setuptools_scm --strip-dev`

po-update:
	pybabel extract --charset=utf-8 -c "TRANSLATORS:" -w 120 -k lazy_gettext -F babel.cfg -o messages.pot codex_of_the_damned
	pybabel update -l ${BABEL_LANG} -w 120 --init-missing -i messages.pot -d codex_of_the_damned/translations

po-compile:
	pybabel compile -D messages -d codex_of_the_damned/translations

po: po-update po-compile

check-porcelain:
	@test -z "`git status --porcelain`" && echo "git clean" || $(error git unclean)

clean:
	rm -rf "codex_of_the_damned.egg-info"
	rm -rf dist

release-local: check-porcelain clean
	check-manifest
	git tag "${NEXT_VERSION}"
	python -m build

release: release-local
	git push origin "${NEXT_VERSION}"
	twine upload -r testpypi dist/*
	twine upload dist/*

test:
	black --check codex_of_the_damned tests
	ruff check
	pytest

update:
	pip install --upgrade --upgrade-strategy eager -e ".[dev]"
