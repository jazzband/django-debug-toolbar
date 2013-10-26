# Make file to compress and join all JS files
all: compress_js compress_css

flake8:
	flake8 *.py debug_toolbar example tests

test:
	pip install Django
	python runtests.py

compress_js:
	yuicompressor debug_toolbar/static/debug_toolbar/js/jquery.js > debug_toolbar/static/debug_toolbar/js/toolbar.min.js
	yuicompressor debug_toolbar/static/debug_toolbar/js/toolbar.js >> debug_toolbar/static/debug_toolbar/js/toolbar.min.js

compress_css:
	yuicompressor --type css debug_toolbar/static/debug_toolbar/css/toolbar.css > debug_toolbar/static/debug_toolbar/css/toolbar.min.css
