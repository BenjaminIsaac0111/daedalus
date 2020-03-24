import pandas as pd

from vivarium.framework.engine import Builder
from vivarium.framework.population import SimulantData
from vivarium.framework.event import Event


class Population:
    """
    This is a common pattern found in Vivarium. Configuration is declared as a class variable for components. In this case
    it defines a parameter space for age when the population is initially generated.
    """
    configuration_defaults = {
        'population': {
            # The range of ages to be generated in the initial population
            'age_start': 0,
            'age_end': 100,
            # Note: There is also a 'population_size' key.
        },
    }

    def __init__(self):
        self.name = 'base_population'

    def setup(self, builder: Builder):
        self.columns = ['PID', 'Area', 'DC1117EW_C_SEX', 'DC1117EW_C_AGE', 'DC2101EW_C_ETHPUK11']

        self.population_view = builder.population.get_view(self.columns)

        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=self.columns)

    # This will be modified to read our synthetic population data from phase 2 of SPENSER.
    def on_initialize_simulants(self, pop_data: SimulantData):
        df = pd.read_csv('data/ass_E09000001_MSOA11_2011.csv')

        len(df)

        df = df[self.columns]

        self.population_view.update(df)
