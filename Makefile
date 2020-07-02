.PHONY: po-update po-compile po

po-update:
	pybabel -v extract -F src/babel.cfg -k lazy_gettext -o messages.pot src
	pybabel -v update -i messages.pot -d src/translations

po-compile:
	pybabel compile -d src/translations

po: po-update po-compile
