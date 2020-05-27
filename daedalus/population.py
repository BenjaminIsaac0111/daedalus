import pandas as pd
import numpy as np

from vivarium.framework.engine import Builder
from vivarium.framework.population import SimulantData
from vivarium.framework.event import Event


class Population:

    # XXX move this to the config file?
    path2file = "../data/Testfile_002.csv"
    mycounter = 0

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

        self.config = builder.configuration

        self.columns = ['PID', 'Area', 'DC1117EW_C_SEX', 'DC1117EW_C_AGE', 'DC2101EW_C_ETHPUK11', 'entrance_time', 'alive', 'resident']
        builder.population.initializes_simulants(self.on_initialize_simulants, 
                                                 creates_columns=self.columns)
        self.population_view = builder.population.get_view(self.columns)
        builder.event.register_listener('time_step', self.age_simulants)

    def on_initialize_simulants(self, pop_data: SimulantData):
        population = pd.read_csv(self.path2file)
        population["DC1117EW_C_AGE"] = population["DC1117EW_C_AGE"].astype(np.float)
        population['alive'] = 'alive'
        population['resident'] = 'yes'
        population['entrance_time'] = pop_data.creation_time
        population = population[self.columns]

        self.population_view.update(population)

    def age_simulants(self, event: Event):
        self.output_results(event)
        population = self.population_view.get(event.index, query="resident == 'yes' & alive == 'alive'")
        population['DC1117EW_C_AGE'] += event.step_size / pd.Timedelta(days=365)
        self.population_view.update(population)
    
    def output_results(self, event):
        """output results at each time-step
        XXX user-defined time steps to output results
        XXX The last filter can be used in the simulation
        """
        self.mycounter += 1

        if self.mycounter == 1:
            fio_population = open("population.txt", "w")
            fio_mortality = open("mortality.txt", "w")
            fio_migration = open("migration.txt", "w")
        else:
            fio_population = open("population.txt", "a+")
            fio_mortality = open("mortality.txt", "a+")
            fio_migration = open("migration.txt", "a+")

        population = self.population_view.get(event.index, query="alive == 'dead'")
        fio_mortality.writelines(str(len(population)) + "\n")
        population = self.population_view.get(event.index, query="resident == 'no'")
        fio_migration.writelines(str(len(population)) + "\n")
        population = self.population_view.get(event.index, query="resident == 'yes' & alive == 'alive'")
        fio_population.writelines(str(len(population)) + "\n")