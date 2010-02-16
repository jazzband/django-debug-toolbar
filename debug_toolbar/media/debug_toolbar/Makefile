# Make file to compress and join all JS files
all: compress_js compress_css

compress_js:
	java -jar ~/bin/yuicompressor.jar js/toolbar.js > js/toolbar.min.js

compress_css:
	java -jar ~/bin/yuicompressor.jar --type css css/toolbar.css > css/toolbar.min.css
