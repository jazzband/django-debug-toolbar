# Make file to compress and join all JS files
all: compress_js compress_css

.PHONY: flake8 example test compress_js compress_css translatable_strings update_translations

flake8:
	flake8 debug_toolbar example tests

example:
	PYTHONPATH=. django-admin.py runserver --settings=example.settings

test:
	PYTHONPATH=. django-admin.py test --settings=tests.settings tests

compress_js:
	yuicompressor debug_toolbar/static/debug_toolbar/js/jquery.js > debug_toolbar/static/debug_toolbar/js/toolbar.min.js
	yuicompressor debug_toolbar/static/debug_toolbar/js/toolbar.js >> debug_toolbar/static/debug_toolbar/js/toolbar.min.js

compress_css:
	yuicompressor --type css debug_toolbar/static/debug_toolbar/css/toolbar.css > debug_toolbar/static/debug_toolbar/css/toolbar.min.css

translatable_strings:
	cd debug_toolbar && django-admin.py makemessages -l en --no-wrap --no-obsolete
	@echo "Please commit changes and run 'tx push -s' (or wait for Transifex to pick them)"

update_translations:
	tx pull
	cd debug_toolbar && django-admin.py compilemessages
