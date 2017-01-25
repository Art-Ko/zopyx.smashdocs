install:
	virtualenv .
	bin/python setup.py develop

test:
	NO_CERT_VERIFICATION=1 bin/pytest zopyx
