import os
from setuptools import setup, find_packages

version = '0.1.0'

setup(name='zopyx.smashdocs',
      version=version,
      description="Smashdocs API wrapper",
      long_description=open(os.path.join("docs", "source", "README.rst")).read() + "\n" +
      open(os.path.join("docs", "source", "HISTORY.rst")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/zopyx.smashdocs',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx'],
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest', 'tox'],
      install_requires=[
          'setuptools',
          'requests',
          'pyjwt',
          'furl',
      ],
      )
