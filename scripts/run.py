#!/usr/bin/env python3
from pathlib import Path
import time
import pandas as pd

import daedalus.utils as utils

from vivarium import InteractiveContext
from vivarium_public_health.population.spenser_population import TestPopulation
from vivarium_public_health.population import FertilityAgeSpecificRates
from vivarium_public_health.population import Mortality
from vivarium_public_health.population import Emigration
from vivarium_public_health.population import ImmigrationDeterministic as Immigration
from vivarium_public_health.population.spenser_population import transform_rate_table
from vivarium_public_health.population.spenser_population import compute_migration_rates

from daedalus.RateTables.EmigrationRateTable import EmigrationRateTable
from daedalus.RateTables.MortalityRateTable import MortalityRateTable
from daedalus.RateTables.FertilityRateTable import FertilityRateTable
from daedalus.RateTables.ImmigrationRateTable import ImmigrationRateTable

def main(configuration):
    """ Run the daedalus Microsimulation """

    # Set up the components using the configuration.

    # TODO: test population initialisation with all West Yorkshire regions.
    #  - The code for this is in daedalus/PopulationSynthesis/*.
    #  - Make sure if region population files already exist in the cache then no need to run initialisation.
    start_population_size = len(pd.read_csv(configuration.paths.path_to_pop_file))
    print('Start Population Size: {}'.format(start_population_size))

    configuration.update({
        'population': {
            'population_size': start_population_size,
            'age_start': 0,
            'age_end': 100,
        }
    }, source=str(Path(__file__).resolve()))

    components = [TestPopulation(),
                  FertilityAgeSpecificRates(),
                  Mortality(),
                  Emigration(),
                  Immigration()]

    simulation = InteractiveContext(components=components,
                                    configuration=configuration,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    num_days = 365 * 2

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
    simulation._data.write("cause.all_causes.cause_specific_immigration_rate",
                           asfr_immigration.rate_table)
    simulation._data.write("cause.all_causes.cause_specific_total_immigrants_per_year",
                           asfr_immigration.total_immigrants)

    simulation.setup()
    simulation.run_for(duration=pd.Timedelta(days=num_days))
    print(simulation.get_population())


if __name__ == "__main__":
    main(configuration=utils.get_config())
