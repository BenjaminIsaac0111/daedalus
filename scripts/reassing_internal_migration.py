#!/usr/bin/env python3
import os
import pandas as pd
import argparse


def reassing_internal_migration(location, input_path, list_pop_locations_dir):
    """ Function that run the ONS-Simmulation comparisons for a given location

    Parameters
    ----------
    location: str
        LAD code for place to run the simulation
    input_path: str
        Input data path where the outputs of all simulations are found
    list_pop_locations_dir:
        list of other locations where to search for internal migration

    """

    input_location_path = os.path.join(input_path, location)
    # path to the simulation files
    list_pop_dir = [i for i in os.listdir(input_location_path) if i.startswith('year_')]

    # for each year run the comparisons
    for year_dir in list_pop_dir:

        simulation_data = pd.read_csv(os.path.join(input_location_path, year_dir,
                                                   'ssm_' + location + '_MSOA11_ppp_2011_simulation_' + year_dir + '.csv'))

        simulation_data['duplicate'] = False
        simulation_data['internal_migration_in'] = 'No'

        for loc in list_pop_locations_dir:
            if loc==location:
                continue
            data_location_simulation = pd.read_csv(os.path.join(input_path, loc, year_dir,
                                                                'ssm_' + loc + '_MSOA11_ppp_2011_simulation_' + year_dir + '.csv'))

            data_location_simulation = data_location_simulation[data_location_simulation['location'] == location]

            if data_location_simulation.shape[0]>0:
                print ('Reassign ',data_location_simulation.shape[0],' individuals that migrated from ',loc,' to ',location)
                data_location_simulation['duplicate'] = True
                data_location_simulation['internal_migration_in'] = 'Yes'

                simulation_data = pd.concat([simulation_data,data_location_simulation])

        simulation_data.to_csv(os.path.join(input_location_path, year_dir,
                                            'ssm_' + location + '_MSOA11_ppp_2011_simulation_' + year_dir + '_reassigned.csv'))

    # run comparison for the total simmulation
    final_file = 'ssm_' + location + '_MSOA11_ppp_2011_simulation.csv'

    simulation_data = pd.read_csv(os.path.join(input_location_path, final_file))

    for loc in list_pop_locations_dir:
        data_location_simulation = pd.read_csv(os.path.join(input_path, loc,
                                                            'ssm_' + loc + '_MSOA11_ppp_2011_simulation.csv'))

        data_location_simulation = data_location_simulation[data_location_simulation['location'] == location]
        data_location_simulation['duplicate'] = True
        data_location_simulation['internal_migration_in'] = 'Yes'

        simulation_data = pd.concat([simulation_data, data_location_simulation])

    simulation_data.to_csv(os.path.join(input_location_path, year_dir,
                                        'ssm_' + location + '_MSOA11_ppp_2011_simulation_reassigned.csv'))


def run_all_validations(input_data_dir):
    """
    Run validation comparison in all existing locations present in an input directory

    input_data_dir : string
        Input data path where the outputs of all simulations are found
    """

    list_pop_locations_dir = [i for i in os.listdir(input_data_dir) if i.startswith('E')]

    for location in list_pop_locations_dir:
        print('Running re-assigment for: ', location)
        reassing_internal_migration(location, input_data_dir, list_pop_locations_dir)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reassign internal migrants to their new location for validation purposes")

    parser.add_argument('--input_data_dir', help='directory where the input data is', default=None)
    parser.add_argument('--location', help='LAD code (in case you want to run a specific location)', default=None)

    args = parser.parse_args()
    if args.location:
        list_pop_locations_dir = [i for i in os.listdir(args.input_data_dir) if i.startswith('E')]
        reassing_internal_migration(args.location, args.input_data_dir, list_pop_locations_dir)
    else:
        run_all_validations(args.input_data_dir)
