install:
	virtualenv .
	bin/python setup.py develop

release:
	mkrelease -d pypi

test:
	bin/pytest zopyx

coverage:
	bin/pytest --cov=zopyx --cov-report annotate --cov-report html zopyx

