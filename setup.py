#!/usr/bin/env python3

import setuptools

def readme():
  with open('README.md') as f:
    return f.read()

def read_reqs():
 with open('requirements.txt') as f:
   return [pkg.rstrip('\n') for pkg in f]

setuptools.setup(
  name='ukpopulation',
  version="1.1.3",
  description='Download, cache, collate, filter, manipulate and extrapolate UK population and household estimates/projections',
  long_description=readme(),
  long_description_content_type="text/markdown",
  url='https://github.com/nismod/ukpopulation',
  author='Andrew P Smith, Tom Russell',
  author_email='a.p.smith@leeds.ac.uk, tom.russell@ouce.ox.ac.uk',
  packages=setuptools.find_packages(),
  install_requires=read_reqs(),
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ),
  test_suite='nose.collector',
  tests_require=['nose']
)
