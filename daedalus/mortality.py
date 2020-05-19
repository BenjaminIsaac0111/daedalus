import numpy as np
import pandas as pd

from vivarium.framework.engine import Builder
from vivarium.framework.event import Event


class Mortality:

    def __init__(self):
        self.name = 'mortality'

    def setup(self, builder: Builder):
        self.config = builder.configuration.mortality
        self.population_view = builder.population.get_view(['alive'], query="alive == 'alive'")
        self.randomness = builder.randomness.get_stream('mortality')
        self.mortality_rate = builder.value.register_rate_producer('mortality_rate', source=self.base_mortality_rate)

        builder.event.register_listener('time_step', self.determine_deaths)

    # In an actual simulation, we’d inform the base mortality rate with data specific to the age, sex, location,
    # year (and potentially other demographic factors) that represent each simulant.
    def base_mortality_rate(self, index: pd.Index) -> pd.Series:
        return pd.Series(self.config.mortality_rate, index=index)

    def determine_deaths(self, event: Event):
        effective_rate = self.mortality_rate(event.index)
        effective_probability = 1 - np.exp(-effective_rate)
        draw = self.randomness.get_draw(event.index)
        affected_simulants = draw < effective_probability
        self.population_view.update(pd.Series('dead', index=event.index[affected_simulants]))
        print(self.population_view.subview('alive') == 'dead')
