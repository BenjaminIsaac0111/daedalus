#!/usr/bin/env python

"""Migration component"""

import numpy as np
import pandas as pd

from vivarium.framework.engine import Builder
from vivarium.framework.event import Event
from vivarium.framework.population import SimulantData

class Migration:

    def __init__(self):
        self.name = 'migration'

    def setup(self, builder: Builder):
        self.columns = ['DC1117EW_C_SEX','resident']

        self.config = builder.configuration.migration
        self.population_view = builder.population.get_view(self.columns, query="resident == 'yes'")
        self.randomness = builder.randomness.get_stream('migration')
        self.migration_rate = builder.value.register_rate_producer('migration_rate', 
                                                                    source=self.base_migration_rate)

        builder.event.register_listener('time_step', self.determine_migration)

    def base_migration_rate(self, index: pd.Index) -> pd.Series:
        return pd.Series(self.config.migration_rate, index=index)
    
    def determine_migration(self, event: Event):
        effective_rate = self.migration_rate(event.index)
        effective_probability = 1 - np.exp(-effective_rate)
        draw = self.randomness.get_draw(event.index)
        affected_simulants = draw < effective_probability

        self.population_view.update(pd.Series('no', 
                                              index=event.index[affected_simulants], name='resident'))