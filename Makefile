all:
	virtualenv .
	bin/python setup.py develop

test:
	bin/pytest zopyx
