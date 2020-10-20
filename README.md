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

Daedalus can be run via command line. In these tutorials, we use the following command:

:warning: This takes ~XXX minutes to finish.

```bash
python scripts/run.py -c config/default_config.yaml --location E08000032 --input_data_dir data --persistent_data_dir persistent_data --output_dir output
```

The following command displays all available options:

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