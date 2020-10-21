#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

with open("requirements.txt", "r") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

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
      install_requires=REQUIRED_PACKAGES,
      # NOTE: vivarium is not available via conda so needs to be installed via pip
      # install_requires=['distutils_pytest', 'vivarium>=0.9.1',
      #                   #'ukcensusapi @ git+https://github.com/BenjaminIsaac0111/UKCensusAPI.git@Development#egg=ukcensusapi',
      #                   #'ukpopulation @ git+https://github.com/nismod/ukpopulation.git@Development#egg=ukpopulation',
      #                   #'humanleague @ git+https://github.com/BenjaminIsaac0111/humanleague.git@Development#egg=humanleague',
      #                   #'household_microsynth @ git+https://github.com/nismod/household_microsynth.git@Development#egg=household_microsynth',
      #                   #'microsimulation @ git+https://github.com/nismod/microsimulation.git@Development#egg=microsimulation',
      #                   'vivarium_public_health @ git+https://github.com/alan-turing-institute/vivarium_public_health_spenser.git@feature/51-assign-MSO-to-immigrants#egg=vivarium_public_health_spenser'],

      test_suite='nose.collector',
      tests_require=['nose'],
      )
