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


def run_pipeline():
    '''

    Given an basic input config file and extra information from the CLI configure the
     vivarium public health spenser pipeline and run it.
    '''

    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    parser.add_argument('--location', help='LAD code')
    parser.add_argument('--input_data_dir', help='directory where the input data is')
    parser.add_argument('--persistent_data_dir', help='directory where the persistent data is')
    parser.add_argument('--output_dir', type=str, help='directory where the output data is saved')

    args = parser.parse_args()
    configuration = utils.get_config(args.config)

    ## get the extra information obtained from the CLI
    if args.location:
        location = args.location
        configuration.update({
            'configuration': {
                'location': args.location,
            }}, source=str(Path(__file__).resolve()))
    else:
        try:
            location = configuration.configuration.location
        except:
            raise RuntimeError('There is no location information in the default '
                               'config file, please provide one with the --location flag')


    if args.input_data_dir:
        input_data_dir = args.input_data_dir
        configuration.update({
            'input_data_dir': input_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            input_data_dir = configuration.input_data_dir
        except:
            raise RuntimeError('There is no input_data_dir information in the default '
                  'config file, please provide one with the --input_data_dir flag')

    if args.persistent_data_dir:
        persistent_data_dir = args.persistent_data_dir
        configuration.update({
            'persistent_data_dir': persistent_data_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            persistent_data_dir = configuration.persistent_data_dir
        except:
            raise RuntimeError('There is no persistent_data_dir information in the default '
                  'config file, please provide one with the --persistent_data_dir flag')

    if args.output_dir:
        output_dir = args.output_dir
        configuration.update({
            'output_dir': output_dir,
        }, source=str(Path(__file__).resolve()))
    else:
        try:
            output_dir = configuration.output_dir
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
        yaml.dump(configuration.to_dict(), config_file)
        print("Write config file successful")

    # add extra information to the config file that is needed for the RunPipeline function
    configuration.update({

        'path_to_raw_pop_file': "{}/{}".format(input_data_dir, input_data_raw_filename),
        'path_to_pop_file': "{}/{}".format(run_output_dir, input_data_processed_filename),
        'path_to_mortality_file': "{}/{}".format(persistent_data_dir, configuration.mortality_file),
        'path_to_fertility_file': "{}/{}".format(persistent_data_dir, configuration.fertility_file),
        'path_to_emigration_file': "{}/{}".format(persistent_data_dir, configuration.emigration_file),
        'path_to_immigration_file': "{}/{}".format(persistent_data_dir, configuration.immigration_file),
        'path_to_total_population_file': "{}/{}".format(persistent_data_dir, configuration.total_population_file),
        'path_msoa_to_lad': "{}/{}".format(persistent_data_dir, configuration.msoa_to_lad),
        'path_to_OD_matrices': "{}/{}".format(persistent_data_dir, configuration.OD_matrix_dir),
        'path_to_OD_matrix_index_file': "{}/{}/{}".format(persistent_data_dir, configuration.OD_matrix_dir,
                                                          configuration.OD_matrix_index_file),
        'path_to_internal_outmigration_file': "{}/{}".format(persistent_data_dir,
                                                             configuration.internal_outmigration_file),
        'path_to_immigration_MSOA': "{}/{}".format(persistent_data_dir, configuration.immigration_MSOA),

    }, source=str(Path(__file__).resolve()))

    # process the raw input data into a VPH format with the right variables
    utils.prepare_dataset(configuration.path_to_raw_pop_file, configuration.path_to_pop_file,
                          location_code=location,
                          lookup_ethnicity="{}/{}".format(persistent_data_dir, configuration.ethnic_lookup),
                          loopup_location_code=configuration.path_msoa_to_lad)

    # run the pipeline
    pop = RunPipeline(configuration)

    # save the output file to csv
    output_data_filename = 'ssm_' + location + '_MSOA11_ppp_2011_simulation.csv'
    pop.to_csv(os.path.join(run_output_dir, output_data_filename))

    # print some summary stats on the simulation
    print('alive', len(pop[pop['alive'] == 'alive']))
    print('dead', len(pop[pop['alive'] == 'dead']))
    print('emigrated', len(pop[pop['alive'] == 'emigrated']))
    print('internal migration', len(pop[pop['previous_MSOA_locations'] != '']))
    print('New children', len(pop[pop['parent_id'] != -1]))
    print('Immigrants', len(pop[pop['immigrated'].astype(str) == 'Yes']))


if __name__ == "__main__":
    run_pipeline()
