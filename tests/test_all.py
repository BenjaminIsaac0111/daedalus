import unittest

from vivarium import InteractiveContext

import daedalus.static as Static
import daedalus.static_h as StaticH
import daedalus.assignment as Assignment


class Test(unittest.TestCase):

    def test_1_static(self):
        region = "E09000001"
        resolution = "MSOA11"
        variant = "ppp"
        cache = "./cache"
        microsim = Static.SequentialMicrosynthesis(region, resolution, variant, False, cache, "./data", True)
        microsim.run(2011, 2011)

    def test_2_static_h(self):
        region = "E09000001"
        resolution = "OA11"
        # requires output from upstream model household
        cache_dir = "./cache"
        upstream_dir = "../household_microsynth/data/"
        input_dir = "./persistent_data/"
        downstream_dir = "./data/"
        microsim = StaticH.SequentialMicrosynthesisH(region, resolution, cache_dir, upstream_dir, input_dir,
                                                     downstream_dir)
        microsim.run(2011, 2011)

    def test_3_assignment(self):
        region = "E09000001"
        h_res = "OA11"
        p_res = "MSOA11"
        variant = "ppp"
        year = 2011
        strict_mode = False
        data_dir = "./data"
        assign = Assignment.Assignment(region, h_res, p_res, year, variant, strict_mode, data_dir)
        assign.run()
        # self.assertTrue(False)

    def test_4_simulation(self):
        # TODO is there a way to set the spec with the population size before running?
        sim = InteractiveContext('config/model_specification.yaml')
        print(sim.get_population().head(100))
        print(len(sim.get_population()))
        self.assertTrue((len(sim.get_population().head()) == 5))
