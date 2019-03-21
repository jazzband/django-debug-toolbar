.PHONY: flake8 example test coverage translatable_strings update_translations

style:
	isort -rc debug_toolbar example tests
	black debug_toolbar example tests setup.py
	flake8 debug_toolbar example tests

style_check:
	isort -rc -c debug_toolbar example tests
	black --target-version=py34 --check debug_toolbar example tests setup.py

flake8:
	flake8 debug_toolbar example tests

example:
	python example/manage.py runserver

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint debug_toolbar/static/debug_toolbar/js/*.js

node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

test:
	DJANGO_SETTINGS_MODULE=tests.settings \
		python -m django test $${TEST_ARGS:-tests}

test_selenium:
	DJANGO_SELENIUM_TESTS=true DJANGO_SETTINGS_MODULE=tests.settings \
		python -m django test $${TEST_ARGS:-tests}

coverage:
	python --version
	coverage erase
	DJANGO_SETTINGS_MODULE=tests.settings \
		coverage run -m django test -v2 $${TEST_ARGS:-tests}
	coverage report
	coverage html

translatable_strings:
	cd debug_toolbar && python -m django makemessages -l en --no-obsolete
	@echo "Please commit changes and run 'tx push -s' (or wait for Transifex to pick them)"

update_translations:
	tx pull -a --minimum-perc=10
	cd debug_toolbar && python -m django compilemessages
