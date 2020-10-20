import pytest
import yaml
import pandas as pd
from os.path import exists
from daedalus.VphSpenserPipeline.ValidationEstimates import compare_summary_estimates
import os

def test_compare_summary_estimates():

    #simulation_data_file = os.path.join('tests','data','ssm_E08000032_MSOA11_ppp_2011_simulation.csv')
    simulation_data_file = os.path.join('tests','data','ssm_E08000033_MSOA11_ppp_2011_simulation.csv')

    ONS_data_file = os.path.join('persistent_data','MYEB3_summary_components_of_change_series_UK_(2019_geog20).csv')

    simulation_data = pd.read_csv(simulation_data_file)
    ONS_data = pd.read_csv(ONS_data_file)

    summary_df = compare_summary_estimates(simulation_data,ONS_data,'E08000033',3)

    assert (summary_df.shape[0]==1)
