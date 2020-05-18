[![DOI](https://zenodo.org/badge/232834194.svg)](https://zenodo.org/badge/latestdoi/232834194)


# Daedalus

Daedalus is a novel dynamic spatial microsimulation prototype being developed at the Leeds Institute for Institute Data Analytics. Currently, the main goal is to a create a proof of concept component as part of the SPENSER (Synthetic Population Estimation and Scenario Projection Model) project.  In this we hope to demonstrate a potential for a highly integrated system that allows users to produce (custom) population projections for policy intervention analysis.

# How to install and run. 
The Daedalus setup.py should install the correct versions but I tell you this just in case; If you have any issue installing the dependencies then please let me know. I have found installing the dependancies is a lot more manageable by using **pip install on the each of the development branches** for the components in SPENSER. Doing this avoids confusion between the versions on PyPi and Conda which are not the latest versions used by this project, I hope to resolve this as some point but for now this offers the most flexbilty.

Example; if you need to install the UKpopulation component then either clone its repo and within the cloned directory, do a 

`pip install .` 

or install using 

`pip install -e ukpopulation @ git+https://github.com/nismod/ukpopulation.git@Development#egg=ukpopulation`

Currently there are a set of unittests being used to work with testing and development. They are somewhat limited at the moment but should allow you to work with the code. It is also possible to work in the interactive mode made availible by the Vivairum component. If you have a look inside the test_all.py you should find test_4_simulation. There are also some other tests to run both the static(h) micro-simulation to generate the initial data from SPENSER as well as a test for running the household/person assignment algorithm(taken from the old static microsimulation).




