import pandas as pd

from vivarium.framework.engine import Builder
from vivarium.framework.population import SimulantData
from vivarium.framework.event import Event


class Population:
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

        self.columns = ['PID', 'Area', 'DC1117EW_C_SEX', 'DC1117EW_C_AGE', 'DC2101EW_C_ETHPUK11', 'entrance_time']

        self.population_view = builder.population.get_view(self.columns)

        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=self.columns)

    def on_initialize_simulants(self, pop_data: SimulantData):
        population = pd.read_csv('data/Testfile.csv')
        population['alive'] = 'alive'
        population['entrance_time'] = pop_data.creation_time
        population = population[self.columns]

        self.population_view.update(population)

    def age_simulants(self, event: Event):
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['DC1117EW_C_AGE'] += event.step_size / pd.Timedelta(days=365)
        self.population_view.update(population)
