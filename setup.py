#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

with open("requirements.txt", "r") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

setup(name='daedalus',
      version='0.0.2',
      description='Microsimulation package for custom UK population projection',
      long_description=readme(),
      url='https://github.com/alan-turing-institute/daedalus',
      author='Benjamin Isaac Wilson, Camila Rangel Smith, Kasra Hosseini',
      author_email='crangelsmith@turing.ac.uk',
      license='MIT',
      packages=['daedalus'],
      zip_safe=False,
      install_requires=REQUIRED_PACKAGES,
      test_suite='nose.collector',
      tests_require=['nose'],
      )
