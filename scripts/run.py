#!/usr/bin/env python3
from pathlib import Path
import time
import pandas as pd
import datetime
import daedalus.utils as utils

from vivarium import InteractiveContext
from vivarium_public_health.population.spenser_population import TestPopulation
from vivarium_public_health.population import FertilityAgeSpecificRates
from vivarium_public_health.population import Mortality
from vivarium_public_health.population import Emigration
from vivarium_public_health.population import ImmigrationDeterministic as Immigration
from vivarium_public_health.population.spenser_population import transform_rate_table
from vivarium_public_health.population.spenser_population import compute_migration_rates
from vivarium_public_health.population import InternalMigration

from daedalus.RateTables.EmigrationRateTable import EmigrationRateTable
from daedalus.RateTables.MortalityRateTable import MortalityRateTable
from daedalus.RateTables.FertilityRateTable import FertilityRateTable
from daedalus.RateTables.ImmigrationRateTable import ImmigrationRateTable
from daedalus.RateTables.InternalMigrationMatrix import InternalMigrationMatrix
from daedalus.RateTables.InternalMigrationRateTable import InternalMigrationRateTable

def main(configuration):
    """ Run the daedalus Microsimulation """

    # Set up the components using the configuration.

    # TODO: test population initialisation with all West Yorkshire regions.
    #  - The code for this is in daedalus/PopulationSynthesis/*.
    #  - Make sure if region population files already exist in the cache then no need to run initialisation.
    utils.prepare_dataset(configuration.paths.path_to_raw_pop_file, configuration.paths.path_to_pop_file)

    start_population_size = len(pd.read_csv(configuration.paths.path_to_pop_file))
    print('Start Population Size: {}'.format(start_population_size))

    configuration.update({
        'population': {
            'population_size': start_population_size,
            'age_start': 0,
            'age_end': 100,
        }
    }, source=str(Path(__file__).resolve()))


    components = [TestPopulation(),Immigration(),
                  FertilityAgeSpecificRates(),Mortality(),Emigration()]
                #,,InternalMigration()
                #  Mortality(),
                #  Emigration(),
                #  Immigration(),
                #  InternalMigration()]

    simulation = InteractiveContext(components=components,
                                    configuration=configuration,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    num_days = 365*2

    # setup internal migration matrices

    OD_matrices = InternalMigrationMatrix(configuration=configuration)
    OD_matrices.set_matrix_tables()
    simulation._data.write("internal_migration.MSOA_index", OD_matrices.MSOA_location_index)
    simulation._data.write("internal_migration.LAD_index", OD_matrices.LAD_location_index)
    simulation._data.write("internal_migration.MSOA_LAD_indices", OD_matrices.df_OD_matrix_with_LAD)
    simulation._data.write("internal_migration.path_to_OD_matrices", configuration.paths.path_to_OD_matrices)

    simulation._data.write("cause.all_causes.immigration_to_MSOA", pd.read_csv(configuration.path_to_immigration_MSOA))

    # setup internal migraionts rates
    asfr_int_migration = InternalMigrationRateTable(configuration=configuration)
    asfr_int_migration.set_rate_table()
    simulation._data.write("cause.age_specific_internal_outmigration_rate", asfr_int_migration.rate_table)

    # setup mortality rates
    asfr_mortality = MortalityRateTable(configuration=configuration)
    asfr_mortality.set_rate_table()
    simulation._data.write("cause.all_causes.cause_specific_mortality_rate",
                           asfr_mortality.rate_table)

    # setup fertility rates
    asfr_fertility = FertilityRateTable(configuration=configuration)
    asfr_fertility.set_rate_table()
    simulation._data.write("covariate.age_specific_fertility_rate.estimate",
                           asfr_fertility.rate_table)

    # setup emigration rates

    asfr_emigration = EmigrationRateTable(configuration=configuration)
    asfr_emigration.set_rate_table()
    simulation._data.write("covariate.age_specific_migration_rate.estimate",
                           asfr_emigration.rate_table)

    # setup immigration rates
    asfr_immigration = ImmigrationRateTable(configuration=configuration)
    asfr_immigration.set_rate_table()
    asfr_immigration.set_total_immigrants()
    simulation._data.write("cause.all_causes.cause_specific_immigration_rate",
                           asfr_immigration.rate_table)
    simulation._data.write("cause.all_causes.cause_specific_total_immigrants_per_year",
                           asfr_immigration.total_immigrants)

    print ('Start simulation setup')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    simulation.setup()

    print ('Start running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    simulation.run_for(duration=pd.Timedelta(days=num_days))

    print('Finished running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    pop = simulation.get_population()
    print(pop.head())

    pop.to_csv('./output/test_output.csv')

    print ('alive',len(pop[pop['alive']=='alive']))
    print ('dead',len(pop[pop['alive']=='dead']))
    print ('emigrated',len(pop[pop['alive']=='emigrated']))
    print ('internal migration',len(pop[pop['previous_MSOA_locations']!='']))
    print ('New children',len(pop[pop['parent_id']!=-1]))
    print ('Immigrants',len(pop[pop['MSOA'].astype(str)=='nan']))



if __name__ == "__main__":
    main(configuration=utils.get_config())
