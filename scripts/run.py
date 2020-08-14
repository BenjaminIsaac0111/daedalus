#!/usr/bin/env python3
from pathlib import Path
import time
import pandas as pd

import daedalus.static as Static
import daedalus.utils as utils

from vivarium import InteractiveContext
from vivarium_public_health.population.spenser_population import TestPopulation
from vivarium_public_health.population import FertilityAgeSpecificRates
from vivarium_public_health.population import Mortality
from vivarium_public_health.population import Emigration
from vivarium_public_health.population import ImmigrationDeterministic as Immigration
from vivarium_public_health.population.spenser_population import transform_rate_table
from vivarium_public_health.population.spenser_population import compute_migration_rates


def main(configuration):
    """ Run the daedalus Microsimulation """

    # Set up the components using the configuration.

    # TODO: test population initialisation with all West Yorkshire regions.

    # TODO: If regions already exist in the cache then no need to run initialisation.
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

    # DEV: limit to population. Need to rename TestPopulation.
    # components = [TestPopulation()]

    simulation = InteractiveContext(components=components,
                                    configuration=configuration,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    num_days = 365 * 2

    # setup mortality rates
    mortality_rate_df = pd.read_csv(configuration.paths.path_to_mortality_file)
    asfr_data = transform_rate_table(mortality_rate_df, 2011, 2012, configuration.population.age_start,
                                     configuration.population.age_end)
    simulation._data.write("cause.all_causes.cause_specific_mortality_rate", asfr_data)

    # setup fertility rates
    fertility_rate_df = pd.read_csv(configuration.paths.path_to_fertility_file)
    asfr_data_fertility = transform_rate_table(fertility_rate_df, 2011, 2012, 10, 50, [2])
    simulation._data.write("covariate.age_specific_fertility_rate.estimate", asfr_data_fertility)

    # setup emigration rates
    df_emigration = pd.read_csv(configuration.paths.path_to_emigration_file)
    df_total_population = pd.read_csv(configuration.paths.path_to_total_population_file)
    asfr_data_emigration = compute_migration_rates(df_emigration, df_total_population, 2011, 2012,
                                                   configuration.population.age_start, configuration.population.age_end)
    simulation._data.write("covariate.age_specific_migration_rate.estimate", asfr_data_emigration)

    # setup immigration rates
    df_immigration = pd.read_csv(configuration.paths.path_to_immigration_file)
    asfr_data_immigration = compute_migration_rates(df_immigration, df_total_population,
                                                    2011,
                                                    2012,
                                                    configuration.population.age_start,
                                                    configuration.population.age_end,
                                                    normalize=False
                                                    )

    # read total immigrants from the file
    total_immigrants = int(df_immigration[df_immigration.columns[4:]].sum().sum())

    simulation._data.write("cause.all_causes.cause_specific_immigration_rate", asfr_data_immigration)
    simulation._data.write("cause.all_causes.cause_specific_total_immigrants_per_year", total_immigrants)

    simulation.setup()
    simulation.run_for(duration=pd.Timedelta(days=num_days))
    pop = simulation.get_population()


if __name__ == "__main__":
    main(configuration=utils.get_config())
