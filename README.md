<div align="center">
    <h1>Daedalus</h1>
</div>
 
<p align="center">
    <!--- <a href="https://zenodo.org/badge/latestdoi/232834194">
        <img alt="DOI" src="https://zenodo.org/badge/232834194.svg">
    </a> --->
    <a href="https://travis-ci.com/alan-turing-institute/daedalus.svg?branch=develop">
        <img alt="Travis" src="https://travis-ci.com/alan-turing-institute/daedalus.svg?branch=develop">
    </a>
    <a href="https://github.com/alan-turing-institute/daedalus/blob/develop/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>

*Daedalus* is a novel dynamic spatial microsimulation pipeline that allows users to produce (custom) population projections for policy intervention analysis.
Currently, it provides simulation utilities for the whole of the United Kingdom at the local authority (LA) level.

*Daedalus* is being developed in collaboration between Leeds Institute for Data Analytics and [the Alan Turing Institute](https://www.turing.ac.uk/) as 
part of the SPENSER (Synthetic Population Estimation and Scenario Projection Model) project.

Table of contents
-----------------

- [Installation and setup](#installation)
- [Tutorials](#tutorials)
    * [Run Daedalus via command line](#run-daedalus-via-command-line)
    * [Speeding up simulations over several LADs by parallelization](#speeding-up-simulations-over-several-lads-by-parallelization)
    * [Evaluate the results](#evaluate-the-results)
    * [Plot the results](#plot-the-results)

# Installation 

We strongly recommend installation via Anaconda:

* Refer to [Anaconda website and follow the instructions](https://docs.anaconda.com/anaconda/install/).

* Create a new environment for *Daedalus*:

```bash
conda create -n daedalus python=3.7
```

* Activate the environment:

```bash
conda activate daedalus
```

* Clone *Daedalus* source code:

```bash
git clone https://github.com/alan-turing-institute/daedalus.git
```

* Install *Daedalus* and its dependencies:

```
cd /path/to/my/daedalus
pip install -v -e .
```

# Tutorials

## Run Daedalus via command line

*Daedalus* can be run via command line. The following command displays all available options:

```bash
python scripts/run.py --help
```

Output:

```bash
usage: run.py [-h] -c config-file [--location LOCATION]
              [--input_data_dir INPUT_DATA_DIR]
              [--persistent_data_dir PERSISTENT_DATA_DIR]
              [--output_dir OUTPUT_DIR]

Dynamic Microsimulation

optional arguments:
  -h, --help            show this help message and exit
  -c config-file, --config config-file
                        the model config file (YAML)
  --location LOCATION   LAD code
  --input_data_dir INPUT_DATA_DIR
                        directory where the input data is
  --persistent_data_dir PERSISTENT_DATA_DIR
                        directory where the persistent data is
  --output_dir OUTPUT_DIR
                        directory where the output data is saved
```

For example, to run a simulation for LAD `E08000032`:

:warning: This takes around 2 to 3 hours (depending on your machine) to finish.

```bash
python scripts/run.py -c config/default_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output
```

In the above command:

* -c: the model config file in YAML format. For more information on the configuration file, 
refer to [section: Configuration file](#configuration-file).
* --location: target LAD code, here `E08000032`. Note that, *Daedalus* can be run in parallel for several LADs, 
refer to [section: Speeding up simulations over several LADs by parallelization](#speeding-up-simulations-over-several-lads-by-parallelization)
* --input_data_dir: the parent directory where population file is stored, e.g., `data` where `ssm_E08000032_MSOA11_ppp_2011.csv` is located.
* --persistent_data_dir: the parent directory that contains all persistent data, e.g., rates, OD matrices and etc,
refer to [section: Preparing datasets](#preparing-datasets) for details.
* --output_dir: directory where the output files will be stored.

As an example, when running the above command, *Daedalus* store the results in the following directory structure:

XXX

with the following messages on the terminal:

```text
❯ python scripts/run.py -c config/default_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output                                                                                                                                                                                                        ─╯

Start Population Size: 524213
Write config file successful

Write the dataset at: output_single/E08000032/ssm_E08000032_MSOA11_ppp_2011_processed.csv
Computing immigration OD matrices...
Computing internal migration rate table...
Caching rate table...
Cached to persistent_data/internal_migration_rate_table_1.csv
Computing mortality rate table...
Caching rate table...
Cached to persistent_data/mortality_rate_table_1.csv
Computing fertility rate table...
Caching rate table...
Cached to persistent_data/fertility_rate_table_1.csv
Computing emigration rate table...
Caching rate table...
Cached to persistent_data/emigration_rate_table_1.csv
Computing immigration rate table...
Caching rate table...
Cached to persistent_data/immigration_rate_table_E08000032_1.csv
Computing total immigration number for location E08000032
Start simulation setup
2020-10-30 10:18:26
2020-10-30 10:18:26.363 | DEBUG    | vivarium.framework.values:register_value_modifier:373 - Registering metrics.1.population_manager.metrics as modifier to metrics
2020-10-30 11:05:54.951 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline int_outmigration_rate
.
.
.
```

## Speeding up simulations over several LADs by parallelization

In the previous [section](#run-daedalus-via-command-line), we ran the simulation over one LAD (specified by `--location E08000032`).
The simulation took around 2 to 3 hours to finish. 
To speed up the simulations over severals LADs, *Daedalus* can be run in parallel. 
For example, the following command runs various LAD codes (specified by  `--path_pop_files "data/ssm_*ppp*csv"`, wildcard accepted) 
on five processes in parallel (specified by `--process_np 5`):

```bash
python scripts/parallel_run.py -c config/default_config.yaml --path_pop_files "data/ssm_*ppp*csv" --input_data_dir data --persistent_data_dir persistent_data --output_dir output --process_np 5
```

In this command:

* -c: the model config file in YAML format. For more information on the configuration file, 
refer to [section: Configuration file](#configuration-file).
* --path_pop_files: path to population files, wildcard accepted. 
LAD codes are extracted from the filenames specified in this argument, e.g., 
in the example, `--path_pop_files "data/ssm_*ppp*csv"`, LAD codes of all files `ssm_*ppp*csv` will be used. 
* --input_data_dir: the parent directory where population file is stored, e.g., `data` where `ssm_*ppp*csv` are located.
* --persistent_data_dir: the parent directory that contains all persistent data, e.g., rates, OD matrices and etc,
refer to [section: Preparing datasets](#preparing-datasets) for details.
* --output_dir: directory where the output files will be stored.
* --process_np: number of processors to be used.
All detected LAD codes will be distributed over the requested number of processes.

The following command displays all available options:

```bash
python scripts/parallel_run.py --help
```

## Evaluate and plot the results

After running the simulation in [section: Run Daedalus via command line](#run-daedalus-via-command-line), 
the results are stored in a directory specified by `--output_dir`, e.g., `output` in the command above.
In our example, it contains the following files:

```bash
XXX
```

To evaluate the results, we need to:
1. reassign the migrants to the correct LADs. 
For example, people who migrated from `LAD_code_1 ---> LAD_code_2` should be added to the population file of `LAD_code_2`.
This step is required since *Daedalus* works and stores the results at LAD level.
2. run validation code on the resulting population files.

The above two steps can be run via one command line:

```bash
XXX
python scripts/validation.py --simulation_dir output --persistent_data_dir persistent_data
```

* --simulation_dir: directory where the simulated population files are stored, i.e., 
output directory of a *Daedalus* simulation.
* --persistent_data_dir: the parent directory that contains the following ONS files: 
    - MYEB2_detailed_components_of_change_series_EW_(2019_geog20).csv 
    - MYEB3_summary_components_of_change_series_UK_(2019_geog20).csv

:warning: Note that the above command requires the following directory structure 
(created by *Daedalus* command line in [section: Run Daedalus via command line](#run-daedalus-via-command-line)):

```bash
XXX
output
└── E08000032
    ├── config_file_E08000032.yml
    ├── ssm_E08000032_MSOA11_ppp_2011_processed.csv
    └── ssm_E08000032_MSOA11_ppp_2011_simulation.csv
    └── year_1
          └── ssm_E08000032_MSOA11_ppp_2011_simulation_year_1.csv
    └── year_2
          └── ssm_E08000032_MSOA11_ppp_2011_simulation_year_2.csv
```

The following command displays all available options:

```bash
python scripts/validation.py --help
```

XXXX

Next, we will evaluate and plot the results in this [notebook](https://github.com/BenjaminIsaac0111/daedalus/blob/feature/refactoring_pipeline/notebooks/pipeline_results_evaluation_plots.ipynb).

<p align="center">
<img src="./figs/fig1.png" width="70%">
</p>

In another [notebook](https://github.com/BenjaminIsaac0111/daedalus/blob/feature/refactoring_pipeline/notebooks/pipeline_results_maps.ipynb),
the results are plotted on maps. 
We use the `cartopy` library to plot maps in this notebook. 
`cartopy` is not installed by default. Please follow the instructions here:

https://scitools.org.uk/cartopy/docs/latest/installing.html

<p align="center">
<img src="./figs/fig2.png" width="50%">
</p>

<p align="center">
<img src="./figs/fig3.png" width="50%">
</p>

## Configuration file

XXX

## Preparing datasets

XXX

## Warning ⚠️

If you are planning to run the microsimulation pipeline on the LADs 
'E09000001', 'E09000033',  'E06000052' and 'E06000053' beware that these are not treated independently 
on the rates as the rest of LADs. They are merged together in the following way: 

- 'E09000001+E09000033'
- 'E06000052+E06000053'

You should be able to run on the single LAD files independently, 
but beware that the pipeline will be using the rates and total immigrated values for those LADs combined. 
The most appropriate way to deal with this is to run the microsimulation from a combined LAD starting file, 
instead of individually. 

E.g for the LADs E09000001 and E09000033:

1. Create a file named: `ssm_E09000001+E09000033_MSOA11_ppp_2011.csv` that contains 
the starting population from both E09000001 and E09000033.
2. Run the pipeline in the following way:
`python scripts/run.py -c config/default_config.yaml --location E09000001+E09000033 --input_data_dir data --persistent_data_dir persistent_data --output_dir output`

The equivalent should be done for 'E06000052' and 'E06000053' LADs.

