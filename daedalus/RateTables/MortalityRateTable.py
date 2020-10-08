import pandas as pd

from daedalus.RateTables.BaseHandler import BaseHandler
from os.path import exists
from os import remove


class MortalityRateTable(BaseHandler):
    def __init__(self, configuration):
        super().__init__(configuration=configuration)
        self.filename = 'mortality_rate_table.csv'
        self.rate_table_path = self.rate_table_dir + self.filename
        self.source_file = self.configuration.path_to_mortality_file

    def _build(self):
        df = pd.read_csv(self.source_file)
        print('Computing mortality rate table...')
        self.rate_table = self.transform_rate_table(df,
                                                    2011,
                                                    2012,
                                                    self.configuration.configuration.population.age_start,
                                                    self.configuration.configuration.population.age_end)
