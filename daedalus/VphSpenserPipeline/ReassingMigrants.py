#!/usr/bin/env python3
import os
import pandas as pd
import argparse
from glob import glob
pd.options.mode.chained_assignment = None

columns_dtypes = {'tracked': 'bool', 'immigrated': 'str', 'emigrated': 'str', 'cause_of_death': 'str',
          'years_of_life_lost': 'float64', 'previous_MSOA_locations': 'str', 'internal_outmigration': 'str',
          'last_outmigration_time': 'str', 'previous_LAD_locations': 'str', 'ethnicity': 'str', 'age': 'float64',
          'MSOA': 'str', 'alive': 'str', 'sex': 'float64', 'location': 'str', 'exit_time': 'str',
          'entrance_time': 'str', 'parent_id': 'int64', 'last_birth_time': 'str', 'age_bucket': 'str'}


def get_migrants(input_path, list_pop_locations_dir):
    """ Function that finds all the individuals that internally migrated into a given location

    Parameters
    ----------
    location: str
        LAD code for place to run the simulation
    input_path: str
        Input data path where the outputs of all simulations are found
    list_pop_locations_dir:
        list of other locations where to search for internal migration

    """

    input_location_path = os.path.join(input_path, list_pop_locations_dir[0])
    # path to the simulation files
    list_pop_dir = [i for i in os.listdir(input_location_path) if i.startswith('year_')]

    dict_migrants = {}
    # for each year run the reassigment
    for year_dir in list_pop_dir:
        print ('Get migrants for ', year_dir)

        migrant_data = pd.DataFrame()
        # look in each location finding the individuals that migrated

        if year_dir == list_pop_dir[-1]:
            full_migrant_data= pd.DataFrame()

        for loc in list_pop_locations_dir:

            data_location_simulation = pd.read_csv(os.path.join(input_path, loc, year_dir,
                                                                'ssm_' + loc + '_MSOA11_ppp_2011_simulation_' + year_dir + '.csv'), dtype=columns_dtypes)

            data_location_simulation_int_migrants = data_location_simulation[data_location_simulation['location'] != loc]

            if data_location_simulation_int_migrants.shape[0]>0:
                print ('Found ',data_location_simulation_int_migrants.shape[0],' individuals that migrated' )
                migrant_data = pd.concat([migrant_data,data_location_simulation_int_migrants])

            if year_dir == list_pop_dir[-1]:
                data_location_simulation_full = pd.read_csv(os.path.join(input_path, loc,
                                                                         'ssm_' + loc + '_MSOA11_ppp_2011_simulation.csv'), dtype=columns_dtypes)

                data_location_simulation_full_migrants = data_location_simulation_full[data_location_simulation_full['location'] != loc]
                if data_location_simulation_full_migrants.shape[0] > 0:
                    print('Found ', data_location_simulation_full_migrants.shape[0], ' individuals that migrated')
                    full_migrant_data = pd.concat([full_migrant_data, data_location_simulation_full_migrants])

        dict_migrants[year_dir] = migrant_data

        if year_dir == list_pop_dir[-1]:
            dict_migrants['full'] = full_migrant_data

    # run comparison for the total simmulation
    return dict_migrants


def reassign_internal_migration_to_LAD(location, input_path, pool_migrants):
    """ Function that finds all the individuals that internally migrated into a given location

    Parameters
    ----------
    location: str
        LAD code for place to run the simulation
    input_path: str
        Input data path where the outputs of all simulations are found
    pool_migrants: dict of Dataframe
        Dictionary with pool of migrants from each year

    """

    input_location_path = os.path.join(input_path, location)
    # path to the simulation files
    list_pop_dir = [i for i in os.listdir(input_location_path) if i.startswith('year_')]

    # for each year run the reassignment
    for year_dir in list_pop_dir:
        print ('Reassign for ', year_dir)

        simulation_data = pd.read_csv(os.path.join(input_location_path, year_dir,
                                                   'ssm_' + location + '_MSOA11_ppp_2011_simulation_' + year_dir + '.csv'), dtype=columns_dtypes)

        simulation_data.loc[:,'duplicate'] = False
        simulation_data.loc[:,'internal_migration_in'] = 'No'


        data_location_simulation = pool_migrants[year_dir]

        data_location_simulation = data_location_simulation[data_location_simulation['location'] == location]

        if data_location_simulation.shape[0]>0:
            print ('Reassign ',data_location_simulation.shape[0],' individuals that migrated to ',location)
            data_location_simulation.loc[:,'duplicate'] = True
            data_location_simulation.loc[:,'internal_migration_in'] = 'Yes'

            simulation_data = pd.concat([simulation_data,data_location_simulation])

        simulation_data.to_csv(os.path.join(input_location_path, year_dir,
                                            'ssm_' + location + '_MSOA11_ppp_2011_simulation_' + year_dir + '_reassigned.csv'))

    # run comparison for the total simmulation
    final_file = 'ssm_' + location + '_MSOA11_ppp_2011_simulation'

    simulation_data_full = pd.read_csv(os.path.join(input_location_path,
                                                   'ssm_' + location + '_MSOA11_ppp_2011_simulation.csv'), dtype=columns_dtypes)

    data_location_simulation_full = pool_migrants['full']

    data_location_simulation_full = data_location_simulation_full[data_location_simulation_full['location'] == location]

    if data_location_simulation_full.shape[0] > 0:
        print ('Full dataset')
        print('Reassign ', data_location_simulation_full.shape[0], ' individuals that migrated from  to ', location)

        data_location_simulation_full.loc[:,'duplicate'] = True
        data_location_simulation_full.loc[:,'internal_migration_in'] = 'Yes'

        simulation_data_full = pd.concat([simulation_data_full, data_location_simulation_full])

    simulation_data_full.to_csv(os.path.join(input_location_path,
                                        final_file+'_reassigned.csv'))
