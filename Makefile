.PHONY: flake8 example test coverage translatable_strings update_translations

flake8:
	flake8 debug_toolbar example tests

isort:
	isort -rc debug_toolbar example tests

isort_check_only:
	isort -rc -c debug_toolbar example tests

example:
	DJANGO_SETTINGS_MODULE=example.settings \
		django-admin runserver

test:
	DJANGO_SETTINGS_MODULE=tests.settings \
		django-admin test tests

test_selenium:
	DJANGO_SELENIUM_TESTS=true DJANGO_SETTINGS_MODULE=tests.settings \
		django-admin test tests

coverage:
	coverage erase
	DJANGO_SETTINGS_MODULE=tests.settings \
		coverage run --branch --source=debug_toolbar `which django-admin` test tests
	coverage html

translatable_strings:
	cd debug_toolbar && django-admin makemessages -l en --no-obsolete
	@echo "Please commit changes and run 'tx push -s' (or wait for Transifex to pick them)"

update_translations:
	tx pull -a --minimum-perc=10
	cd debug_toolbar && django-admin compilemessages
