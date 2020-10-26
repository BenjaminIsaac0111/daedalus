#!/usr/bin/env python3
import pandas as pd
import os
from daedalus.utils import get_age_bucket

def compare_summary_estimates(simulation_data, ONS_data, location, n_years, detailed = False):
    '''Function that compares the outputs of the simulation with the estimates from
    the ONS. Total values are compared.
 Parameters
    ----------
    simulation_data : Dataframe
        Input data from the VPH simulation
    ONS_data : Dataframe
        Summary estimates from the ONS existing in the persistent data
    location: str
        LAD code for place to run the simulation
    n_years: int
        Number of years the simulation was ran for
    detailed: bool
        If this function is being used for a age, gender detailed comparison
    '''
    import numpy as np
    np.seterr(divide='ignore', invalid='ignore')

    starting_year = 2011

    ONS_data_LAD = ONS_data[ONS_data['ladcode20'] == location]

    columns = ['population','births','deaths', 'internal_out',  'international_in',
               'international_out']

    years = [(starting_year+year) for year in range(1, n_years + 1)]

    total_values = {}

    total_values["location"] = location
    total_values["year"] = starting_year + n_years
    for col in columns:
        if col == 'population' and detailed==False:
            continue
        count = 0
        for y in years:
            column_name = col + "_" + str(y)
            count = count + ONS_data_LAD[column_name].sum()

        total_values["ONS_total_"+col] = count

    if detailed==False:
        total_values["ONS_total_population"] = ONS_data_LAD["population_" + str(starting_year + n_years)].sum()

    # print some summary stats on the simulation
    total_values["simulation_population"] = len(simulation_data[simulation_data['alive'] == 'alive'])
    total_values["simulation_deaths"] = len(simulation_data[simulation_data['alive'] == 'dead'])
    total_values["simulation_international_out"] = len(simulation_data[simulation_data['alive'] == 'emigrated'])
    total_values["simulation_international_in"] = len(simulation_data[simulation_data['immigrated'].astype(str) == 'Yes'])
    total_values["simulation_internal_out"] = len(simulation_data[simulation_data['internal_outmigration'] == 'Yes'])
    total_values["simulation_births"] = len(simulation_data[simulation_data['parent_id']  != -1])

    for col in columns:
        print (col)
        print (total_values["simulation_"+col] , total_values["ONS_total_"+col])
        total_values["ONS_simulation_"+col+"_diff"] = total_values["simulation_"+col] - total_values["ONS_total_"+col]
        total_values["ONS_simulation_"+col+"_diff_%"] = \
            (total_values["simulation_"+col] - total_values["ONS_total_"+col])/float(total_values["ONS_total_"+col])*100

        print (col, "simulation: ", total_values["simulation_"+col],", ONS estimation ", total_values["ONS_total_"+col])
        print (col, "diff: ", round(total_values["ONS_simulation_"+col+"_diff"],2),"(",round(total_values["ONS_simulation_"+col+"_diff_%"],1),"%)")
        print ()

    return pd.DataFrame.from_dict([total_values])

def compare_detailed_estimates(simulation_data, ONS_data, location, n_years):
    '''Function that compares the outputs of the simulation with the estimates from
    the ONS. Detailed gender and age values are compared.
 Parameters
    ----------
    simulation_data : Dataframe
        Input data from the VPH simulation
    ONS_data : Dataframe
        Summary estimates from the ONS existing in the persistent data
    location: str
        LAD code for place to run the simulation
    n_years: int
        Number of years the simulation was ran for
    '''

    ONS_data = ONS_data[ONS_data['ladcode20'] == location]
    try:
        age_bucket = simulation_data['age_bucket']
    except:
        simulation_data = get_age_bucket(simulation_data)
        age_bucket = simulation_data['age_bucket']
        ONS_data = get_age_bucket(ONS_data)


    df_list = []
    for sex in [1,2]:

        simulation_data_sex = simulation_data[simulation_data['sex']==sex]
        ONS_data_sex = ONS_data[ONS_data['sex']==sex]

        for age in age_bucket:

            simulation_data_sex_age = simulation_data_sex[simulation_data_sex['age_bucket'] == age]
            ONS_data_sex_age = ONS_data_sex[ONS_data_sex['age_bucket'] == age]

            print (age)
            print (sex)
            df = compare_summary_estimates(simulation_data_sex_age, ONS_data_sex_age, location, n_years, True)
            df['age_start'] = simulation_data_sex_age['age'].min()
            df['age_end'] = simulation_data_sex_age['age'].max()
            df['sex'] = sex

            df_list.append(df)

    df_output = pd.concat(df_list)

    return df_output