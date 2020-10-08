#!/usr/bin/env python3
from pathlib import Path
import os
import pandas as pd
import datetime
import daedalus.utils as utils
import argparse
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


def run_vphs_pipeline(config):
    """ Run the daedalus Microsimulation """

    # Set up the components using the config.

    components = [TestPopulation(), Immigration(),
                  InternalMigration(), Mortality(), Emigration(), FertilityAgeSpecificRates()]

    simulation = InteractiveContext(components=components,
                                    configuration=config,
                                    plugin_configuration=utils.base_plugins(),
                                    setup=False)

    num_days = config.configuration.num_days

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

def main():
    parser = argparse.ArgumentParser(description="Dynamic Microsimulation")

    parser.add_argument("-c", "--config", required=True, type=str, metavar="config-file",
                        help="the model config file (YAML)")
    parser.add_argument('--location', type=str, nargs='1', default='E08000032',
                        help='LAD code')
    parser.add_argument('--ndays', type=int, nargs='1', default=365,
                        help='number of days to run the ')
    parser.add_argument('--step_size', type=int, nargs='1', default=10,
                        help='number of days to run the ')
    parser.add_argument('--input_data_dir', type=str, nargs='1', default='.data',
                        help='number of days to run the ')
    parser.add_argument('--persistant_data_dir', type=str, nargs='1', default='.persistent_data',
                        help='number of days to run the ')
    parser.add_argument('--output_dir', type=str, nargs='1', default='.output',
                        help='number of days to run the ')

    # TODO parse/add arguments for synthetic population generation for LADs.
    args = parser.parse_args()
    configuration = utils.get_config(args.config)

    input_data_raw_filename = 'ssm_' + args.location + '_MSOA11_ppp_2011.csv'
    input_data_processed_filename = 'ssm_' + args.location + '_MSOA11_ppp_2011_processed.csv'

    start_population_size = len(pd.read_csv("{}/{}".format(args.input_data_dir, input_data_raw_filename)))
    print('Start Population Size: {}'.format(start_population_size))

    run_output_dir = os.path.join(args.output_dir, args.location + '_output')
    # put output plots in the results dir
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(run_output_dir, exist_ok=True)

    configuration.update({

        'path_to_raw_pop_file': "{}/{}".format(args.input_data_dir, input_data_raw_filename),
        'path_to_pop_file': "{}/{}".format(run_output_dir, input_data_processed_filename),
        'path_to_mortality_file': "{}/{}".format(args.persistant_data_dir, configuration.mortality_file),
        'path_to_fertility_file': "{}/{}".format(args.persistant_data_dir, configuration.fertility_file),
        'path_to_emigration_file': "{}/{}".format(args.persistant_data_dir, configuration.emigration_file),
        'path_to_immigration_file': "{}/{}".format(args.persistant_data_dir, configuration.immigration_file),
        'path_to_total_population_file': "{}/{}".format(args.persistant_data_dir, configuration.total_population_file),
        'path_msoa_to_lad': "{}/{}".format(args.persistant_data_dir, configuration.msoa_to_lad),
        'path_to_OD_matrices': "{}/{}".format(args.persistant_data_dir, configuration.OD_matrix_dir),
        'path_to_OD_matrix_index_file': "{}/{}/{}".format(args.persistant_data_dir, configuration.OD_matrix_dir,
                                                          configuration.OD_matrix_index_file),
        'path_to_internal_outmigration_file': "{}/{}".format(args.persistant_data_dir,
                                                             configuration.InternalOutmig2011_LEEDS2),
        'path_to_immigration_MSOA': "{}/{}".format(args.persistant_data_dir, configuration.immigration_MSOA),

        'population': {
            'population_size': start_population_size,
            'age_start': 0,
            'age_end': 100,
        },
        'time': {
            'step_size': args.step_size,
            'num_days': args.num_days,
        },
        'location': args.location,

    }, source=str(Path(__file__).resolve()))

    utils.prepare_dataset(configuration.path_to_raw_pop_file, configuration.path_to_pop_file,
                          location_code=args.location,
                          lookup_ethnicity="{}/{}".format(args.persistant_data_dir, configuration.ethnic_lookup),
                          loopup_location_code=configuration.path_msoa_to_lad)



    pop = run_vphs_pipeline(configuration)


    output_data_filename = 'ssm_' + args.location + '_MSOA11_ppp_2011_simulation.csv'
    pop.to_csv(os.path.join(run_output_dir,output_data_filename))

    print('alive', len(pop[pop['alive'] == 'alive']))
    print('dead', len(pop[pop['alive'] == 'dead']))
    print('emigrated', len(pop[pop['alive'] == 'emigrated']))
    print('internal migration', len(pop[pop['previous_MSOA_locations'] != '']))
    print('New children', len(pop[pop['parent_id'] != -1]))
    print('Immigrants', len(pop[pop['immigrated'].astype(str) == 'Yes']))


if __name__ == "__main__":
    main()
