import unittest

from vivarium import InteractiveContext

import daedalus.static as Static
import daedalus.static_h as StaticH
import daedalus.assignment as Assignment
import pandas as pd


class Test(unittest.TestCase):

    def test_static_Bradford(self):
        region = "E08000032"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
        microsim.run(2011, 2012)

    def test_static_Calderdale(self):
        region = "E08000033"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
        microsim.run(2011, 2012)

    def test_static_Kirklees(self):
        region = "E08000034"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
        microsim.run(2011, 2012)

    def test_static_leeds(self):
        region = "E08000035"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
        microsim.run(2011, 2012)

    def test_static_wakefield(self):
        region = "E08000036"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", False)
        microsim.run(2011, 2012)

    # def test_1_static(self):
    #     region = "E09000001"
    #     resolution = "MSOA11"
    #     variant = "ppp"
    #     cache_dir = "./tests/cache"
    #     microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache_dir, "./tests/data", True)
    #     microsim.run(2011, 2011)
    #
    # def test_2_static_household(self):
    #     region = "E09000001"
    #     resolution = "OA11"
    #     cache_dir = "./tests/cache"
    #     # Normally requires output from upstream model household_micro
    #     upstream_dir = "./tests/data"
    #     input_dir = "./persistent_data/"
    #     downstream_dir = "./tests/data/"
    #     microsim = StaticH.SequentialMicrosynthesisH(region, resolution, cache_dir, upstream_dir, input_dir,
    #                                                  downstream_dir)
    #     microsim.run(2011, 2011)
    #
    # def test_3_assignment(self):
    #     region = "E09000001"
    #     h_res = "OA11"
    #     p_res = "MSOA11"
    #     variant = "ppp"
    #     year = 2011
    #     strict_mode = False
    #     data_dir = "./tests/data"
    #     assign = Assignment.Assignment(region, h_res, p_res, year, variant, strict_mode, data_dir)
    #     assign.run()

    def test_4_simulation(self):
        # TODO is there a way to set the spec with the population size before running? There is!
        sim = InteractiveContext('config/model_specification.yaml', setup=False)
        sim.configuration.update({'population': {'population_size': len(pd.read_csv('data/Testfile.csv'))}})
        sim.setup()
        sim.run()
        print(sim.get_population())
