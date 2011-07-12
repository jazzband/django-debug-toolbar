# Make file to compress and join all JS files
all: compress_js compress_css

compress_js:
	java -jar ~/bin/yuicompressor.jar debug_toolbar/media/debug_toolbar/js/jquery.js > debug_toolbar/media/debug_toolbar/js/toolbar.min.js
	java -jar ~/bin/yuicompressor.jar debug_toolbar/media/debug_toolbar/js/toolbar.js >> debug_toolbar/media/debug_toolbar/js/toolbar.min.js

compress_css:
	java -jar ~/bin/yuicompressor.jar --type css debug_toolbar/media/debug_toolbar/css/toolbar.css > debug_toolbar/media/debug_toolbar/css/toolbar.min.css
