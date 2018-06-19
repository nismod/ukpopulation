#!/usr/bin/env python3

from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

setup(name='ukpopulation',
  version='1.0.1',
  description='Download, collate, cache, and query Population projections',
  long_description=readme(),
  url='https://github.com/nismod/ukpopulation',
  author='Andrew P Smith, Tom Russell',
  author_email='a.p.smith@leeds.ac.uk, tom.russell@ouce.ox.ac.uk',
  license='MIT',
  packages=['ukpopulation'],
  zip_safe=False,
  install_requires=['distutils_pytest', 'ukcensusapi'],
  dependency_links=['git+git://github.com/virgesmith/UKCensusAPI.git#egg=ukcensusapi'],
  test_suite='nose.collector',
  tests_require=['nose'],
  python_requires='>=3'
)
