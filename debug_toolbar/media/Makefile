# Make file to compress and join all JS files
all: compress_js compress_css

compress_js:
	java -jar ~/bin/yuicompressor.jar toolbar.js > toolbar.min.js
	java -jar ~/bin/yuicompressor.jar jquery.cookie.js >> toolbar.min.js

compress_css:
	java -jar ~/bin/yuicompressor.jar --type css toolbar.css > toolbar.min.css
