#!/usr/bin/env python3
import pandas as pd
import datetime
import daedalus.utils as utils

from vivarium import InteractiveContext
from vivarium_public_health.population.spenser_population import TestPopulation
from vivarium_public_health.population import FertilityAgeSpecificRates
from vivarium_public_health.population import Mortality
from vivarium_public_health.population import Emigration
from vivarium_public_health.population import ImmigrationDeterministic as Immigration
from vivarium_public_health.population import InternalMigration

from daedalus.RateTables.EmigrationRateTable import EmigrationRateTable
from daedalus.RateTables.MortalityRateTable import MortalityRateTable
from daedalus.RateTables.FertilityRateTable import FertilityRateTable
from daedalus.RateTables.ImmigrationRateTable import ImmigrationRateTable
from daedalus.RateTables.InternalMigrationMatrix import InternalMigrationMatrix
from daedalus.RateTables.InternalMigrationRateTable import InternalMigrationRateTable


def RunPipeline(config):
    """ Run the daedalus Microsimulation pipeline

   Parameters
    ----------
    config : ConfigTree
        Config file to run the pipeline

    Returns:
    --------
     A dataframe with the resulting simulation
    """


    # Set up the components using the config.

    components = [TestPopulation(), Immigration(),
                  InternalMigration(), Mortality(), Emigration(), FertilityAgeSpecificRates()]

    simulation = InteractiveContext(components=components,
                                    configuration=config,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    num_days = config.configuration.time.num_days

    # setup internal migration matrices

    OD_matrices = InternalMigrationMatrix(configuration=config)
    OD_matrices.set_matrix_tables()
    simulation._data.write("internal_migration.MSOA_index", OD_matrices.MSOA_location_index)
    simulation._data.write("internal_migration.LAD_index", OD_matrices.LAD_location_index)
    simulation._data.write("internal_migration.MSOA_LAD_indices", OD_matrices.df_OD_matrix_with_LAD)
    simulation._data.write("internal_migration.path_to_OD_matrices", config.path_to_OD_matrices)

    simulation._data.write("cause.all_causes.immigration_to_MSOA", pd.read_csv(config.path_to_immigration_MSOA))

    # setup internal migraionts rates
    asfr_int_migration = InternalMigrationRateTable(configuration=config)
    asfr_int_migration.set_rate_table()
    simulation._data.write("cause.age_specific_internal_outmigration_rate", asfr_int_migration.rate_table)

    # setup mortality rates
    asfr_mortality = MortalityRateTable(configuration=config)
    asfr_mortality.set_rate_table()
    simulation._data.write("cause.all_causes.cause_specific_mortality_rate",
                           asfr_mortality.rate_table)

    # setup fertility rates
    asfr_fertility = FertilityRateTable(configuration=config)
    asfr_fertility.set_rate_table()
    simulation._data.write("covariate.age_specific_fertility_rate.estimate",
                           asfr_fertility.rate_table)

    # setup emigration rates

    asfr_emigration = EmigrationRateTable(configuration=config)
    asfr_emigration.set_rate_table()
    simulation._data.write("covariate.age_specific_migration_rate.estimate",
                           asfr_emigration.rate_table)

    # setup immigration rates
    asfr_immigration = ImmigrationRateTable(configuration=config)
    asfr_immigration.set_rate_table()
    asfr_immigration.set_total_immigrants()
    simulation._data.write("cause.all_causes.cause_specific_immigration_rate",
                           asfr_immigration.rate_table)
    simulation._data.write("cause.all_causes.cause_specific_total_immigrants_per_year",
                           asfr_immigration.total_immigrants)

    print('Start simulation setup')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    simulation.setup()

    print('Start running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    simulation.run_for(duration=pd.Timedelta(days=num_days))

    print('Finished running simulation')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    pop = simulation.get_population()

    return pop
