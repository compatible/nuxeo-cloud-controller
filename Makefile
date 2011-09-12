.PHONY: test setup-env

install:
	python setup.py install

test: env
	env/bin/python ncc/__init__.py halt
	env/bin/python ncc/__init__.py clean
	env/bin/python ncc/__init__.py boot
	nosetests -v

env:
	env/bin/pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run "source env/bin/activate"

setup-env:
	env/bin/pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run "source env/bin/activate"

clean:
	find . -name "*.pyc" | xargs rm -f
	rm -rf build ncc.egg-info dist
	env/bin/python ncc/__init__.py clean

tidy: clean
	rm -rf env

push:
	echo "Not yet"
	#rsync -avz -e ssh src Makefile dependencies.txt crawl.sh \
	#	nuxeo@styx.nuxeo.com:/var/www/home.nuxeo.org/
