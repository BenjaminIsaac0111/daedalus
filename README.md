<div align="center">
    <h1>Daedalus</h1>
</div>
 
<p align="center">
    <a href="https://zenodo.org/badge/latestdoi/232834194">
        <img alt="DOI" src="https://zenodo.org/badge/232834194.svg">
    </a>
    <a href="https://github.com/BenjaminIsaac0111/daedalus/blob/master/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>

Daedalus is a novel dynamic spatial microsimulation pipeline that allows users to produce (custom) population projections for policy intervention analysis.
Currently, it provides simulation utilities for the whole of the United Kingdom at the local authority (LA) level.

Daedalus is being developed in collaboration between Leeds Institute for Institute Data Analytics and the Alan Turing Institute as 
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

* Create a new environment for daedalus

```bash
conda create -n daedalus python=3.7
```

* Activate the environment:

```bash
conda activate daedalus
```

* Clone daedalus source code:

```bash
git clone https://github.com/BenjaminIsaac0111/daedalus.git 
```

* Install daedalus and its dependencies:

```
cd /path/to/my/daedalus
pip install -v -e .
```

# Tutorials

## Run Daedalus via command line

Daedalus can be run via command line. The following command displays all available options:

```bash
python scripts/run.py --help
```

and the output is:

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

In these tutorials, we use the following command:

:warning: This takes ~XXX minutes to finish.

```bash
python scripts/run.py -c config/default_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output
```

Expected output:

```text
❯ python scripts/run.py -c config/default_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output
Start Population Size: 524213
Write config file successful

Write the dataset at: output/E08000032/ssm_E08000032_MSOA11_ppp_2011_processed.csv
Computing immigration rate table...
Computing internal migration rate table...
Caching rate table...
Cached to persistent_data/integral_migration_rate_table.csv
Computing mortality rate table...
Caching rate table...
Cached to persistent_data/mortality_rate_table.csv
Computing fertility rate table...
Caching rate table...
Cached to persistent_data/fertility_rate_table.csv
Computing emigration rate table...
Caching rate table...
Cached to persistent_data/emigration_rate_table.csv
Fetching rate table from catch persistent_data/immigration_rate_table_E08000032.csv
Computing total immigration number for location E08000032
Start simulation setup
2020-10-20 12:04:50
2020-10-20 12:04:50.422 | DEBUG    | vivarium.framework.values:register_value_modifier:373 - Registering metrics.1.population_manager.metrics as modifier to metrics
2020-10-20 12:29:13.249 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline int_outmigration_rate
2020-10-20 12:53:14.599 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline mortality_rate
2020-10-20 13:16:42.556 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline emigration_rate
2020-10-20 13:24:55.896 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline fertility rate
2020-10-20 13:24:55.896 | DEBUG    | vivarium.framework.values:_register_value_producer:323 - Registering value pipeline metrics
2020-10-20 13:26:39.657 | DEBUG    | vivarium.framework.engine:step:140 - 2011-01-01 00:00:00
2020-10-20 13:27:57.277 | DEBUG    | vivarium.framework.engine:step:140 - 2011-01-11 00:00:00
2020-10-20 13:28:54.614 | DEBUG    | vivarium.framework.engine:step:140 - 2011-01-21 00:00:00
2020-10-20 13:30:03.109 | DEBUG    | vivarium.framework.engine:step:140 - 2011-01-31 00:00:00
2020-10-20 13:31:11.185 | DEBUG    | vivarium.framework.engine:step:140 - 2011-02-10 00:00:00
2020-10-20 13:32:08.721 | DEBUG    | vivarium.framework.engine:step:140 - 2011-02-20 00:00:00
2020-10-20 13:33:11.799 | DEBUG    | vivarium.framework.engine:step:140 - 2011-03-02 00:00:00
2020-10-20 13:34:15.401 | DEBUG    | vivarium.framework.engine:step:140 - 2011-03-12 00:00:00
2020-10-20 13:35:26.567 | DEBUG    | vivarium.framework.engine:step:140 - 2011-03-22 00:00:00
2020-10-20 13:36:27.414 | DEBUG    | vivarium.framework.engine:step:140 - 2011-04-01 00:00:00
2020-10-20 13:37:37.768 | DEBUG    | vivarium.framework.engine:step:140 - 2011-04-11 00:00:00
2020-10-20 13:38:54.107 | DEBUG    | vivarium.framework.engine:step:140 - 2011-04-21 00:00:00
2020-10-20 13:39:53.323 | DEBUG    | vivarium.framework.engine:step:140 - 2011-05-01 00:00:00
2020-10-20 13:41:12.803 | DEBUG    | vivarium.framework.engine:step:140 - 2011-05-11 00:00:00
2020-10-20 13:42:32.034 | DEBUG    | vivarium.framework.engine:step:140 - 2011-05-21 00:00:00
2020-10-20 13:43:44.056 | DEBUG    | vivarium.framework.engine:step:140 - 2011-05-31 00:00:00
2020-10-20 13:44:55.048 | DEBUG    | vivarium.framework.engine:step:140 - 2011-06-10 00:00:00
2020-10-20 13:46:13.413 | DEBUG    | vivarium.framework.engine:step:140 - 2011-06-20 00:00:00
2020-10-20 13:47:17.833 | DEBUG    | vivarium.framework.engine:step:140 - 2011-06-30 00:00:00
2020-10-20 13:48:37.467 | DEBUG    | vivarium.framework.engine:step:140 - 2011-07-10 00:00:00
2020-10-20 13:49:54.801 | DEBUG    | vivarium.framework.engine:step:140 - 2011-07-20 00:00:00
2020-10-20 13:51:21.094 | DEBUG    | vivarium.framework.engine:step:140 - 2011-07-30 00:00:00
2020-10-20 13:52:46.625 | DEBUG    | vivarium.framework.engine:step:140 - 2011-08-09 00:00:00
2020-10-20 13:54:01.570 | DEBUG    | vivarium.framework.engine:step:140 - 2011-08-19 00:00:00
2020-10-20 13:55:06.145 | DEBUG    | vivarium.framework.engine:step:140 - 2011-08-29 00:00:00
2020-10-20 13:56:04.882 | DEBUG    | vivarium.framework.engine:step:140 - 2011-09-08 00:00:00
2020-10-20 13:57:12.043 | DEBUG    | vivarium.framework.engine:step:140 - 2011-09-18 00:00:00
2020-10-20 13:58:07.850 | DEBUG    | vivarium.framework.engine:step:140 - 2011-09-28 00:00:00
2020-10-20 13:59:14.272 | DEBUG    | vivarium.framework.engine:step:140 - 2011-10-08 00:00:00
2020-10-20 14:00:29.067 | DEBUG    | vivarium.framework.engine:step:140 - 2011-10-18 00:00:00
2020-10-20 14:01:45.110 | DEBUG    | vivarium.framework.engine:step:140 - 2011-10-28 00:00:00
2020-10-20 14:02:53.453 | DEBUG    | vivarium.framework.engine:step:140 - 2011-11-07 00:00:00
2020-10-20 14:04:23.663 | DEBUG    | vivarium.framework.engine:step:140 - 2011-11-17 00:00:00
2020-10-20 14:05:29.141 | DEBUG    | vivarium.framework.engine:step:140 - 2011-11-27 00:00:00
2020-10-20 14:06:37.390 | DEBUG    | vivarium.framework.engine:step:140 - 2011-12-07 00:00:00
2020-10-20 14:07:49.889 | DEBUG    | vivarium.framework.engine:step:140 - 2011-12-17 00:00:00
2020-10-20 14:08:51.414 | DEBUG    | vivarium.framework.engine:step:140 - 2011-12-27 00:00:00
Finished running simulation
alive 532578
dead 4121
emigrated 1545
internal migration 16838
New children 9522
Immigrants 4509
```

## Speeding up simulations over several LADs by parallelization

In the previous [section](#run-daedalus-via-command-line), we ran the simulation over one LAD (specified by `--location E08000032`).
The simulation took around XXX minutes. 
To speed up the simulations over severals LADs, Daedalus can be run in parallel. 
For example, the following command line runs daedalus over five LADs in parallel 
(note `--process_np` specifies the number of processes to be run in parallel):

```bash
python scripts/parallel_run.py -c config/default_config.yaml --path_pop_files "data/ssm_*ppp*csv" --input_data_dir data --persistent_data_dir persistent_data --output_dir output --process_np 5
```

The following command displays all available options:

```bash
python scripts/parallel_run.py --help
```

and the output is:

```bash
usage: parallel_run.py [-h] -c config-file [--path_pop_files PATH_POP_FILES]
                       [--pop_start_index POP_START_INDEX]
                       [--pop_end_index POP_END_INDEX]
                       [--input_data_dir INPUT_DATA_DIR]
                       [--persistent_data_dir PERSISTENT_DATA_DIR]
                       [--output_dir OUTPUT_DIR] [--process_np PROCESS_NP]

Run Dynamic Microsimulation in parallel

optional arguments:
  -h, --help            show this help message and exit
  -c config-file, --config config-file
                        the model config file (YAML)
  --path_pop_files PATH_POP_FILES
                        path to population files, wildcard accepted
  --pop_start_index POP_START_INDEX
                        pop_files[pop_start_index:pop_end_index] will be used
  --pop_end_index POP_END_INDEX
                        pop_files[pop_start_index:pop_end_index] will be used.
                        If < 0, all files will be used.
  --input_data_dir INPUT_DATA_DIR
                        directory where the input data is
  --persistent_data_dir PERSISTENT_DATA_DIR
                        directory where the persistent data is
  --output_dir OUTPUT_DIR
                        directory where the output data is saved
  --process_np PROCESS_NP
                        number of processors to be used
```


## Evaluate the results

## Plot the results