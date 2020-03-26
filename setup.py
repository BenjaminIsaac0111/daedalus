#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='daedalus',
      version='0.0.1',
      description='Microsimulation package for custom UK population projection',
      long_description=readme(),
      url='https://github.com/BenjaminIsaac0111/daedalus',
      author='Benjamin Isaac Wilson',
      author_email='medbwila@leeds.ac.uk',
      license='MIT',
      packages=['daedalus'],
      zip_safe=False,

      # NOTE: vivarium is not available via conda so needs to be installed via pip
      install_requires=['distutils_pytest', 'vivarium', 'ukcensusapi', 'ukpopulation'],
      dependency_links=['git+https://github.com/BenjaminIsaac0111/humanleague.git@Development#egg=humanleague',
                        'git+https://github.com/BenjaminIsaac0111/UKCensusAPI.git@Development#egg=ukcensusapi',
                        'git+https://github.com/nismod/household_microsynth.git@Development#egg=household_microsynth',
                        'git+https://github.com/nismod/ukpopulation.git@Development#egg=ukpopulation'],

      test_suite='nose.collector',
      tests_require=['nose'],
      )
