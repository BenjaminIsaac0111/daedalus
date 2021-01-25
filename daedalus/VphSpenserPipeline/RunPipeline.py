#!/usr/bin/env python3
import pandas as pd
import datetime
import daedalus.utils as utils
from pathlib import Path
import os
from vivarium import InteractiveContext
from vivarium_population_spenser.population.spenser_population import TestPopulation
from vivarium_population_spenser.population import FertilityAgeSpecificRates
from vivarium_population_spenser.population import Mortality
from vivarium_population_spenser.population import Emigration
from vivarium_population_spenser.population import ImmigrationDeterministic as Immigration
from vivarium_population_spenser.population import InternalMigration

from daedalus.RateTables.EmigrationRateTable import EmigrationRateTable
from daedalus.RateTables.MortalityRateTable import MortalityRateTable
from daedalus.RateTables.FertilityRateTable import FertilityRateTable
from daedalus.RateTables.ImmigrationRateTable import ImmigrationRateTable
from daedalus.RateTables.InternalMigrationMatrix import InternalMigrationMatrix
from daedalus.RateTables.InternalMigrationRateTable import InternalMigrationRateTable


def RunPipeline(config, start_population_size):
    """ Run the daedalus Microsimulation pipeline

   Parameters
    ----------
    config : ConfigTree
        Config file to run the pipeline
    start_population_size: int
        Size of the starting population
    Returns:
    --------
     A dataframe with the resulting simulation
    """


    # Set up the components using the config.

    config.update({
            'population': {
            'population_size': start_population_size,
        }}, source=str(Path(__file__).resolve()))

    num_years = config.time.num_years


    components = [eval(x) for x in config.components]

    simulation = InteractiveContext(components=components,
                                    configuration=config,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    if 'InternalMigration()' in config.components:
        # setup internal migration matrices
        OD_matrices = InternalMigrationMatrix(configuration=config)
        OD_matrices.set_matrix_tables()
        simulation._data.write("internal_migration.MSOA_index", OD_matrices.MSOA_location_index)
        simulation._data.write("internal_migration.LAD_index", OD_matrices.LAD_location_index)
        simulation._data.write("internal_migration.MSOA_LAD_indices", OD_matrices.df_OD_matrix_with_LAD)
        simulation._data.write("internal_migration.path_to_OD_matrices", config.path_to_OD_matrices)

        # setup internal migraionts rates
        asfr_int_migration = InternalMigrationRateTable(configuration=config)
        asfr_int_migration.set_rate_table()
        simulation._data.write("cause.age_specific_internal_outmigration_rate", asfr_int_migration.rate_table)

    if 'Mortality()' in config.components:
        # setup mortality rates
        asfr_mortality = MortalityRateTable(configuration=config)
        asfr_mortality.set_rate_table()
        simulation._data.write("cause.all_causes.cause_specific_mortality_rate",
                           asfr_mortality.rate_table)

    if 'FertilityAgeSpecificRates()' in config.components:
        # setup fertility rates
        asfr_fertility = FertilityRateTable(configuration=config)
        asfr_fertility.set_rate_table()
        simulation._data.write("covariate.age_specific_fertility_rate.estimate",
                           asfr_fertility.rate_table)

    if 'Emigration()' in config.components:

        # setup emigration rates
        asfr_emigration = EmigrationRateTable(configuration=config)
        asfr_emigration.set_rate_table()
        simulation._data.write("covariate.age_specific_migration_rate.estimate",
                           asfr_emigration.rate_table)

    if 'Immigration()' in config.components:
        # setup immigration rates
        asfr_immigration = ImmigrationRateTable(configuration=config)
        asfr_immigration.set_rate_table()
        asfr_immigration.set_total_immigrants()
        simulation._data.write("cause.all_causes.immigration_to_MSOA", pd.read_csv(config.path_to_immigration_MSOA))
        simulation._data.write("cause.all_causes.cause_specific_immigration_rate",
                           asfr_immigration.rate_table)
        simulation._data.write("cause.all_causes.cause_specific_total_immigrants_per_year",
                           asfr_immigration.total_immigrants)

    print('Start simulation setup')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    simulation.setup()

    print('Start running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    for year in range(1,num_years+1):

        simulation.run_for(duration=pd.Timedelta(days=365.25))

        print('Finished running simulation for year:', year)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        pop = simulation.get_population()

        # assign age brackets to the individuals

        pop = utils.get_age_bucket(pop)

        # save the output file to csv
        year_output_dir = os.path.join(os.path.join(config.output_dir,config.location,'year_'+str(year)))
        os.makedirs(year_output_dir, exist_ok=True)

        output_data_filename = 'ssm_' + config.location + '_MSOA11_ppp_2011_simulation_year_'+str(year)+'.csv'
        pop.to_csv(os.path.join(year_output_dir, output_data_filename))

        print ()
        print ('In year: ',config.time.start.year + year)
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


    return pop
