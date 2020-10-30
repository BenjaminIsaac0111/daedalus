#!/usr/bin/env python3
from pathlib import Path
import os
import vivarium
import pandas as pd
import datetime
import daedalus.utils as utils
import argparse
import yaml
from daedalus.VphSpenserPipeline.RunPipeline import RunPipeline


def run_pipeline(configuration_file, location=None, input_data_dir=None, persistent_data_dir=None, output_dir=None):
    """
    Given an basic input config file and data directory information configure the
     vivarium public health spenser pipeline and run it.

    Parameters
    ----------
    config : ConfigTree
        Config file to run the pipeline
    location: str
        LAD code for place to run the simulation
    input_data_dir: str
        Path to the directory with the input data
    persistent_data_dir: str
        Path to the directory where the rate/probability/demographic files that needed to run the simulation are found.
    output_dir: str
        Path to the directory where the output data should be saved
    """

    config = utils.get_config(configuration_file)

    ## get the input information obtained from the CLI
    if location:
        config.update({
            'location': location,
            }, source=str(Path(__file__).resolve()))
    else:
        try:
            location = config.location
        except:
            raise RuntimeError('There is no location information in the default '
                               'config file, please provide one with the --location flag')


    if input_data_dir:
        config.update({
            'input_data_dir': input_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            input_data_dir = config.input_data_dir
        except:
            raise RuntimeError('There is no input_data_dir information in the default '
                  'config file, please provide one with the --input_data_dir flag')

    if persistent_data_dir:
        persistent_data_dir = persistent_data_dir
        config.update({
            'persistent_data_dir': persistent_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            persistent_data_dir = config.persistent_data_dir
        except:
            raise RuntimeError('There is no persistent_data_dir information in the default '
                  'config file, please provide one with the --persistent_data_dir flag')

    if output_dir:
        output_dir = output_dir
        config.update({
            'output_dir': output_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            output_dir = config.output_dir
        except:
            raise RuntimeError('There is no output_dir information in the default '
                  'config file, please provide one with the --output_dir flag')

    # based on input location, get the input files that will be used in the simulation
    input_data_raw_filename = 'ssm_' + location + '_MSOA11_ppp_2011.csv'
    input_data_processed_filename = 'ssm_' + location + '_MSOA11_ppp_2011_processed.csv'

    start_population_size = len(pd.read_csv("{}/{}".format(input_data_dir, input_data_raw_filename)))
    print('Start Population Size: {}'.format(start_population_size))

    # output directory where all files from the run will be saved
    run_output_dir = os.path.join(output_dir, location)
    # put output plots in the results dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    os.makedirs(run_output_dir, exist_ok=True)

    # save the yml file with the minimal amount of information needed to run this script again and reproduce results
    with open(os.path.join(run_output_dir, 'config_file_'+location+'.yml'), 'w') as config_file:
        yaml.dump(config.to_dict(), config_file)
        print("Write config file successful")

    # add extra information to the config file that is needed for the RunPipeline function
    config.update({

        'path_to_raw_pop_file': "{}/{}".format(input_data_dir, input_data_raw_filename),
        'path_to_pop_file': "{}/{}".format(run_output_dir, input_data_processed_filename),
        'path_to_mortality_file': "{}/{}".format(persistent_data_dir, config.mortality_file),
        'path_to_fertility_file': "{}/{}".format(persistent_data_dir, config.fertility_file),
        'path_to_emigration_file': "{}/{}".format(persistent_data_dir, config.emigration_file),
        'path_to_immigration_file': "{}/{}".format(persistent_data_dir, config.immigration_file),
        'path_to_total_population_file': "{}/{}".format(persistent_data_dir, config.total_population_file),
        'path_msoa_to_lad': "{}/{}".format(persistent_data_dir, config.msoa_to_lad),
        'path_to_OD_matrices': "{}/{}".format(persistent_data_dir, config.OD_matrix_dir),
        'path_to_OD_matrix_index_file': "{}/{}/{}".format(persistent_data_dir, config.OD_matrix_dir,
                                                          config.OD_matrix_index_file),
        'path_to_internal_outmigration_file': "{}/{}".format(persistent_data_dir,
                                                             config.internal_outmigration_file),
        'path_to_immigration_MSOA': "{}/{}".format(persistent_data_dir, config.immigration_MSOA),

    }, source=str(Path(__file__).resolve()))

    # process the raw input data into a VPH format with the right variables
    utils.prepare_dataset(config.path_to_raw_pop_file, config.path_to_pop_file,
                          location_code=location,
                          lookup_ethnicity="{}/{}".format(persistent_data_dir, config.ethnic_lookup),
                          loopup_location_code=config.path_msoa_to_lad)

    # run the pipeline
    pop = RunPipeline(config, start_population_size)

    print('Finished running the full simulation')
    # save the output file to csv
    output_data_filename = 'ssm_' + location + '_MSOA11_ppp_2011_simulation.csv'
    pop.to_csv(os.path.join(run_output_dir, output_data_filename))

 # print some summary stats on the simulation
    print('alive', len(pop[pop['alive'] == 'alive']))

    if 'Mortality()' in config.components:
        print('dead', len(pop[pop['alive'] == 'dead']))
    if 'Emigration()' in config.components:
        print('emigrated', len(pop[pop['alive'] == 'emigrated']))
    if 'InternalMigration()' in config.components:
        print('internal migration', len(pop[pop['internal_outmigration'] != '']))
    if 'FertilityAgeSpecificRates()' in config.components:
        print('New children', len(pop[pop['parent_id'] != -1]))
    if 'Immigration()' in config.components:
        print('Immigrants', len(pop[pop['immigrated'].astype(str) == 'Yes']))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    parser.add_argument('--location', help='LAD code', default=None)
    parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    parser.add_argument('--persistent_data_dir', help='directory where the persistent data is', default=None)
    parser.add_argument('--output_dir', type=str, help='directory where the output data is saved', default=None)

    args = parser.parse_args()
    configuration_file = args.config

    run_pipeline(configuration_file, args.location, args.input_data_dir, args.persistent_data_dir, args.output_dir)
