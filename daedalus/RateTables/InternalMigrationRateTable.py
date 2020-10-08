import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class InternalMigrationRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.filename = 'integral_migration_rate_table.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.path_to_internal_outmigration_file

    def _build(self):
        df_internal_outmigration = pd.read_csv(self.source_file)
        print('Computing internal migration rate table...')

        self.rate_table = self.transform_rate_table(df_internal_outmigration, 2011, 2012,
                                                    self.configuration.configuration.population.age_start,
                                                    self.configuration.configuration.population.age_end)
