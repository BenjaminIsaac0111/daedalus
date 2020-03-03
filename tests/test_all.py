import unittest

from vivarium import InteractiveContext
from daedalus.Population import Population


class MyTestCase(unittest.TestCase):

    def test_simulation(self):
        config = {'randomness': {'key_columns': ['entrance_time', 'age']}}
        sim = InteractiveContext(components=[Population()], configuration=config)
        print(sim.get_population().head(100))
        print(len(sim.get_population()))

        print(sim.get_population().head(100))
        print(len(sim.get_population()))

        sim.step()

        self.assertTrue((len(sim.get_population().head()) == 5))

if __name__ == '__main__':
    unittest.main()
