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
        self.config = builder.configuration

        self.with_common_random_numbers = bool(self.config.randomness.key_columns)
        self.register = builder.randomness.register_simulants

        if self.with_common_random_numbers and not ['entrance_time', 'age'] == self.config.randomness.key_columns:
            raise ValueError("If running with CRN, you must specify ['entrance_time', 'age'] as"
                             "the randomness key columns.")

        self.age_randomness = builder.randomness.get_stream('age_initialization',
                                                            for_initialization=self.with_common_random_numbers)
        self.sex_randomness = builder.randomness.get_stream('sex_initialization')

        columns_created = ['age', 'sex', 'alive', 'entrance_time']
        builder.population.initializes_simulants(self.on_initialize_simulants, creates_columns=columns_created)

        self.population_view = builder.population.get_view(columns_created)

        # This say that at each time step, age the simulants.
        builder.event.register_listener('time_step', self.age_simulants)


    # This will be modified to read our synthetic population data from phase 2 of SPENSER.
    def on_initialize_simulants(self, pop_data: SimulantData):
        age_start = self.config.population.age_start
        age_end = self.config.population.age_end

        if age_start == age_end:
            age_window = pop_data.creation_window / pd.Timedelta(days=365)
        else:
            age_window = age_end - age_start

        age_draw = self.age_randomness.get_draw(pop_data.index)
        age = age_start + age_draw * age_window

        if self.with_common_random_numbers:
            population = pd.DataFrame({'entrance_time': pop_data.creation_time,
                                       'age': age.values}, index=pop_data.index)
            self.register(population)
            population['sex'] = self.sex_randomness.choice(pop_data.index, ['Male', 'Female'])
            population['alive'] = 'alive'
        else:
            population = pd.DataFrame(
                {'age': age.values,
                 'sex': self.sex_randomness.choice(pop_data.index, ['Male', 'Female']),
                 'alive': pd.Series('alive', index=pop_data.index),
                 'entrance_time': pop_data.creation_time},
                index=pop_data.index)
            print("Working..")

        self.population_view.update(population)

    def age_simulants(self, event: Event):
        population = self.population_view.get(event.index, query="alive == 'alive'")
        population['age'] += event.step_size / pd.Timedelta(days=365)
        self.population_view.update(population)
