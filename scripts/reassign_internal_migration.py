#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from glob import glob
from daedalus.VphSpenserPipeline.ReassingMigrants import get_migrants, reassign_internal_migration_to_LAD
pd.options.mode.chained_assignment = None

columns_dtypes = {'tracked': 'bool', 'immigrated': 'str', 'emigrated': 'str', 'cause_of_death': 'str',
          'years_of_life_lost': 'float64', 'previous_MSOA_locations': 'str', 'internal_outmigration': 'str',
          'last_outmigration_time': 'str', 'previous_LAD_locations': 'str', 'ethnicity': 'str', 'age': 'float64',
          'MSOA': 'str', 'alive': 'str', 'sex': 'float64', 'location': 'str', 'exit_time': 'str',
          'entrance_time': 'str', 'parent_id': 'int64', 'last_birth_time': 'str', 'age_bucket': 'str'}




def reassign_all(input_data_dir, startswith = 'E'):
    """
    Run reassigment in all existing locations present in an input directory

    Parameters:
    ----------
    input_data_dir : string
        Input data path where the outputs of all simulations are found
    startswith: string
        Prefix after the directory to be used

    Returns:
    ----------
        A dictionary of dataframes with the pool of migrants for each year.
    """

    # TODO: Change to glob
    list_pop_locations_dir = [i for i in os.listdir(input_data_dir) if i.startswith(startswith)]


    pool_migrants = get_migrants(input_data_dir, list_pop_locations_dir)

    for location in list_pop_locations_dir:
        print ()
        print('Running re-assigment for: ', location)
        reassign_internal_migration_to_LAD(location, input_data_dir, pool_migrants)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reassign internal migrants to their new location for validation purposes")

    parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    parser.add_argument('--location', help='LAD code (in case you want to run a specific location)', default=None)

    args = parser.parse_args()
    if args.location:
        list_pop_locations_dir = [i for i in os.listdir(args.input_data_dir) if i.startswith('E')]
        pool_migrants = get_migrants(args.input_data_dir, list_pop_locations_dir)
        reassign_internal_migration_to_LAD(args.location, args.input_data_dir, pool_migrants)
    else:
        reassign_all(args.input_data_dir)
