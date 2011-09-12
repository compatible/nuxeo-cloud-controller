.PHONY: test serve run setup-env

test: env
	./ncc.py halt
	./ncc.py clean
	./ncc.py boot
	nosetests -v

serve: env
	python src/server.py

run: serve

env:
	pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run "source env/bin/activate"

setup-env:
	pip install --upgrade -s -E env -r deps.txt
	echo "Remember to run "source env/bin/activate"

clean:
	find . -name "*.pyc" | xargs rm -f
	./ncc.py clean

superclean: clean
	rm -f nuxeocloud.db
	rm -rf data/* env

push:
	echo "Not yet"
	#rsync -avz -e ssh src Makefile dependencies.txt crawl.sh \
	#	nuxeo@styx.nuxeo.com:/var/www/home.nuxeo.org/
