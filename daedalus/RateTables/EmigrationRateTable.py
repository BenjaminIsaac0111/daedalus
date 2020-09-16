import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class EmigrationRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.filename = 'emigration_rate_table.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.paths.path_to_emigration_file
        self.total_population_file = self.configuration.paths.path_to_total_population_file

    def _build(self):
        df_emigration = pd.read_csv(self.source_file)
        df_total_population = pd.read_csv(self.total_population_file)
        print('Computing emigration rate table...')
        self.rate_table = self.compute_migration_rates(df_emigration, df_total_population,
                                                       2011,
                                                       2012,
                                                       self.configuration.population.age_start,
                                                       self.configuration.population.age_end)
