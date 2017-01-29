install:
	virtualenv .
	bin/python setup.py develop

test:
	bin/pytest zopyx

coverage:
	bin/pytest --cov=zopyx --cov-report annotate --cov-report html zopyx

