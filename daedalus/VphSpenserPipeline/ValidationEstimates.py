#!/usr/bin/env python3
import pandas as pd
import os

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
            count = count + ONS_data_LAD[column_name].values[0]

        total_values["ONS_total_"+col] = count

    if detailed==False:
        total_values["ONS_total_population"] = ONS_data_LAD["population""_" + str(starting_year + n_years)].values[0]

    # print some summary stats on the simulation
    total_values["simulation_population"] = len(simulation_data[simulation_data['alive'] == 'alive'])
    total_values["simulation_deaths"] = len(simulation_data[simulation_data['alive'] == 'dead'])
    total_values["simulation_international_out"] = len(simulation_data[simulation_data['alive'] == 'emigrated'])
    total_values["simulation_international_in"] = len(simulation_data[simulation_data['immigrated'].astype(str) == 'Yes'])
    total_values["simulation_internal_out"] = len(simulation_data[simulation_data['internal_outmigration'] == 'Yes'])
    total_values["simulation_births"] = len(simulation_data[simulation_data['parent_id']  != -1])

    for col in columns:
        total_values["ONS_simulation_"+col+"_diff"] = total_values["simulation_"+col] - total_values["ONS_total_"+col]
        total_values["ONS_simulation_"+col+"_diff_%"] = \
            (total_values["simulation_"+col+""] - total_values["ONS_total_"+col])/total_values["ONS_total_"+col+""]*100

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

    df_list = []
    for sex in [1,2]:

        simulation_data_sex = simulation_data[simulation_data['sex']==sex]
        ONS_data_sex = ONS_data[ONS_data['sex']==sex]

        for age in range (0,90):

            simulation_data_sex_age = simulation_data_sex[
                    (simulation_data_sex['age'] >= age) & (simulation_data_sex['age'] < age + n_years)]

            ONS_data_sex_age = ONS_data_sex[ONS_data_sex['age'] == age]

            df = compare_summary_estimates(simulation_data_sex_age, ONS_data_sex_age, location, n_years, True)
            df['age_start'] = age
            df['age_end'] = age+n_years
            df['sex'] = sex

            df_list.append(df)

    df_output = pd.concat(df_list)

    return df_output