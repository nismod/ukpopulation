#!/usr/bin/env python3

import setuptools

def readme():
  with open('README.md') as f:
    return f.read()

setuptools.setup(
  name='ukpopulation',
  version='1.1.0',
  description='Download, cache, collate, filter, manipulate and extrapolate UK population and household estimates/projections',
  long_description=readme(),
  long_description_content_type="text/markdown",
  url='https://github.com/nismod/ukpopulation',
  author='Andrew P Smith, Tom Russell',
  author_email='a.p.smith@leeds.ac.uk, tom.russell@ouce.ox.ac.uk',
  packages=setuptools.find_packages(),
  install_requires=["numpy",
                    "pandas",
                    "requests",
                    "openpyxl",
                    "beautifulsoup4",
                    "lxml",
                    "pyexcel",
                    "pyexcel-xls",
                    "pyexcel-xlsx",
                    "ukcensusapi"],
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ),
  test_suite='nose.collector',
  tests_require=['nose']
)
