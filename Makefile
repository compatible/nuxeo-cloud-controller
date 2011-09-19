.PHONY: test setup-env install check clean tidy

test: env
	env/bin/python ncc/main.py halt
	env/bin/python ncc/main.py clean
	nosetests -v

install:
	pip install . --upgrade -r deps.txt

check:
	pyflakes ncc

env:
	pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run 'source env/bin/activate'"

setup-env:
	pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run "source env/bin/activate"

clean:
	find . -name "*.pyc" | xargs rm -f
	rm -rf build ncc.egg-info dist
	env/bin/python ncc/main.py halt
	env/bin/python ncc/main.py clean

tidy: clean
	rm -rf env

push:
	echo "Not yet"
	#rsync -avz -e ssh src Makefile dependencies.txt crawl.sh \
	#	nuxeo@styx.nuxeo.com:/var/www/home.nuxeo.org/
