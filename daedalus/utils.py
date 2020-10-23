"""
utility functions
"""

import argparse
import glob
import yaml
import numpy as np
import os
import pandas as pd
#import humanleague as hl
from scipy.sparse import coo_matrix
import scipy

from vivarium.config_tree import ConfigTree


def get_config(config):

    # Open the vivarium config yaml.
    with open(config) as config_file:
        config = ConfigTree(yaml.full_load(config_file))
    return config

# TODO Investigate the mock artifact manager. Not sure if this is what we should be using.
def base_plugins():
    config = {'required': {
                  'data': {
                      'controller': 'vivarium_public_health.testing.mock_artifact.MockArtifactManager',
                      'builder_interface': 'vivarium.framework.artifact.ArtifactInterface'
                  }
             }
    }
    return ConfigTree(config)


def relEqual(x, y, tol=2 ** -26):
    """
  Simple test for relative equality of floating point within tolerance
  Default tolerance is sqrt double epsilon i.e. about 7.5 significant figures
  """
    if y == 0:
        return x == 0
    return abs(float(x) / float(y) - 1.) < tol


def create_age_sex_marginal(est, lad):
    """
  Generate age-by-sex marginal from estimated (MYE/SNPP) data
  """
    # TODO remove gender and age size hard-coding...
    tmp = est[est.GEOGRAPHY_CODE == lad].drop("GEOGRAPHY_CODE", axis=1)
    marginal = unlistify(tmp, ["GENDER", "C_AGE"], [2, 86], "OBS_VALUE")
    return marginal


# this is a copy-paste from household_microsynth
def unlistify(table, columns, sizes, values):
    """
  Converts an n-column table of counts into an n-dimensional array of counts
  """
    pivot = table.pivot_table(index=columns, values=values)
    # order must be same as column order above
    array = np.zeros(sizes, dtype=int)
    array[tuple(pivot.index.codes)] = pivot.values.flat
    return array


def listify(array, valuename, colnames):
    """
  converts a multidimensional numpy array into a pandas dataframe with colnames[0] referring to dimension 0, etc
  and valuecolumn containing the array values
  """
    multiindex = pd.MultiIndex.from_product([range(i) for i in array.shape])
    colmapping = {"level_" + str(i): colnames[i] for i in range(len(colnames))}

    return pd.DataFrame({valuename: pd.Series(index=multiindex, data=array.flatten())}).reset_index().rename(colmapping,
                                                                                                             axis=1)


# this is a copy-paste from household_microsynth
def remap(indices, mapping):
    """
  Converts array of index values back into category values
  """
    # values = []
    # for i in range(0, len(indices)):
    #   values.append(mapping[indices[i]])

    values = [mapping[indices[i]] for i in range(len(indices))]

    return values


def check_and_invert(columns, excluded):
    """
  Returns the subset of column names that is not in excluded
  """
    if isinstance(excluded, str):
        excluded = [excluded]

    included = columns.tolist()
    for exclude in excluded:
        if exclude in included:
            included.remove(exclude)
    return included


# TODO there is a lot of commonality in the 3 functions below
def cap_value(table, colname, maxval, sumcolname):
    """
  Aggregates values in column colname 
  """
    table_under = table[table[colname] < maxval].copy()
    table_over = \
    table[table[colname] >= maxval].copy().groupby(check_and_invert(table.columns.values, [colname, sumcolname]))[
        sumcolname].sum().reset_index()
    table_over[colname] = maxval

    return table_under.append(table_over, sort=False)


def adjust_mye_age(mye):
    """
  Makes mid-year estimate/snpp data conform with census age categories:
  - subtract 100 from age (so that "1" means under 1)
  - aggregate 86,87,88,89,90,91 into 86 (meaning 85+)
  """
    # keep track of some totals
    pop = mye.OBS_VALUE.sum()
    pop_m = mye[mye.GENDER == 1].OBS_VALUE.sum()
    pop_a = mye[mye.GEOGRAPHY_CODE == "E06000015"].OBS_VALUE.sum()

    # this modifies argument!
    mye.C_AGE -= 100

    mye_adj = mye[mye.C_AGE < 86].copy()
    mye_over85 = mye[mye.C_AGE > 85].copy()

    # print(myeOver85.head(12))

    agg86 = mye_over85.pivot_table(index=["GEOGRAPHY_CODE", "GENDER"], values="OBS_VALUE", aggfunc=sum)
    agg86["C_AGE"] = 86
    agg86 = agg86.reset_index()

    mye_adj = mye_adj.append(agg86, ignore_index=True, sort=False)

    # ensure the totals in the adjusted table match the originals (within precision)
    assert relEqual(mye_adj.OBS_VALUE.sum(), pop)
    assert relEqual(mye_adj[mye_adj.GENDER == 1].OBS_VALUE.sum(), pop_m)
    assert relEqual(mye_adj[mye_adj.GEOGRAPHY_CODE == "E06000015"].OBS_VALUE.sum(), pop_a)

    return mye_adj


def adjust_pp_age(pp):
    """
  Makes (s)npp data conform with census maximum categories:
  - aggregate 85,86,87,88,89,90 into 85 (meaning >=85)
  """
    # keep track of some totals
    pop = pp.OBS_VALUE.sum()
    pop_m = pp[pp.GENDER == 1].OBS_VALUE.sum()
    pop_a = pp[pp.GEOGRAPHY_CODE == "E06000015"].OBS_VALUE.sum()

    # pp.C_AGE += 1

    mye_adj = pp[pp.C_AGE < 85].copy()
    mye_over85 = pp[pp.C_AGE > 84].copy()

    # print(myeOver85.head(12))

    agg86 = mye_over85.pivot_table(index=["GEOGRAPHY_CODE", "GENDER", "PROJECTED_YEAR_NAME"], values="OBS_VALUE",
                                   aggfunc=sum)
    agg86["C_AGE"] = 85
    agg86 = agg86.reset_index()

    mye_adj = mye_adj.append(agg86, ignore_index=True, sort=False)

    # ensure the totals in the adjusted table match the originals (within precision)
    assert relEqual(mye_adj.OBS_VALUE.sum(), pop)
    assert relEqual(mye_adj[mye_adj.GENDER == 1].OBS_VALUE.sum(), pop_m)
    assert relEqual(mye_adj[mye_adj.GEOGRAPHY_CODE == "E06000015"].OBS_VALUE.sum(), pop_a)

    return mye_adj


def check_result(msynth):
    if isinstance(msynth, str):
        raise ValueError(msynth)
    elif not msynth["conv"]:
        print(msynth)
        raise ValueError("convergence failure")


# def microsynthesise_seed(dc1117, dc2101, dc6206):
#     """
#   Microsynthesise a seed population from census data
#   """
#     n_geog = len(dc1117.GEOGRAPHY_CODE.unique())
#     n_sex = 2  # len(dc1117.C_SEX.unique())
#     n_age = len(dc1117.C_AGE.unique())
#     cen11sa = unlistify(dc1117, ["GEOGRAPHY_CODE", "C_SEX", "C_AGE"], [n_geog, n_sex, n_age], "OBS_VALUE")
#     n_eth = len(dc2101.C_ETHPUK11.unique())
#     cen11se = unlistify(dc2101, ["GEOGRAPHY_CODE", "C_SEX", "C_ETHPUK11"], [n_geog, n_sex, n_eth], "OBS_VALUE")
#
#     # TODO use microdata (national or perhaps regional) Mistral/persistent_data/seed_ASE_EW.csv
#     # - requires unified age structure
#
#     # microsynthesise these two into a 4D seed (if this has a lot of zeros can have big impact on microsim)
#     print("Synthesising 2011 seed population...", end='')
#     msynth = hl.qis([np.array([0, 1, 2]), np.array([0, 1, 3])], [cen11sa, cen11se])
#     check_result(msynth)
#     print("OK")
#     return msynth["result"]


def year_sequence(start_year, end_year):
    """
  returns a sequence from start_year to end_year inclusive
  year_sequence(2001,2005) = [2001, 2002, 2003, 2004, 2005]
  year_sequence(2005,2001) = [2005, 2004, 2003, 2002, 2001]
  """
    if start_year == end_year:
        return [start_year]

    if start_year < end_year:
        return list(range(start_year, end_year + 1))

    return list(range(start_year, end_year - 1, -1))


def prepare_dataset(dataset_path="../daedalus/persistent_data/ssm_E08000032_MSOA11_ppp_2011.csv",
                    output_path="./persistent_data/test_ssm_E08000032_MSOA11_ppp_2011.csv",
                    columns_map={"Area": "location",
                                 "DC1117EW_C_SEX": "sex",
                                 "DC1117EW_C_AGE": "age",
                                 "DC2101EW_C_ETHPUK11": "ethnicity"},
                    location_code=None,
                    lookup_ethnicity="./persistent_data/ethnic_lookup.csv",
                    loopup_location_code="./persistent_data/Middle_Layer_Super_Output_Area__2011__to_Ward__2016__Lookup_in_England_and_Wales.csv"):
    """Read in a dataset (normally stored on daedalus) and convert it into a format readable by vivarium

    Args:
        dataset_path (str, optional): path to the original population dataset (normally located at daedalus).
        output_path (str, optional): write the output file in this path.
        columns_map (dict, optional): change the name of columns according to columns_map.
        location_code (str, optional): if specified, set the location code.
        lookup_ethnicity (str, optional): how to map ethnicity from digits to strings.
    """
    # read the dataset
    dataset = pd.read_csv(dataset_path)
    if columns_map:
        # rename columns
        dataset = dataset.rename(columns=columns_map)
    if lookup_ethnicity:
        # map ethnicity from digits to strings as specified in the lookup_ethnicity file
        lookup = pd.read_csv(lookup_ethnicity)
        code_ethnicity = dict(zip(lookup['Base population file (persistent data) From "C_ETHPUK11"'],
                                  lookup['Rate to use (from NewEthpop outputs) Code']))
        dataset.replace({"ethnicity": code_ethnicity}, inplace=True)
    if location_code:
        dataset['MSOA'] = dataset['location']
        dataset['location'] = location_code
    else:
        dataset['MSOA'] = dataset['location']
        lookup = pd.read_csv(loopup_location_code)
        code_LAD = dict(zip(lookup['MSOA11CD'],
                                  lookup['LAD16CD']))
        dataset.replace({"location": code_LAD}, inplace=True)


    dataset.to_csv(output_path, index=False)
    print(f"\nWrite the dataset at: {output_path}")


def make_od_matrices_sparse(path2csv, row_threshold=10):
    """Make OD matrices sparse

    Args:
        path2csv: path to csv files, wildcards are accepted
        row_threshold (int, optional): all values less than row_max / row_threshold will be set to zero. Defaults to 10.
    """

    list_of_files = glob.glob(path2csv)

    for i, fi_rel in enumerate(list_of_files):
        fi = os.path.abspath(fi_rel)
        print(f"Processing: {fi}")
        
        od_weights = pd.read_csv(fi).values
        od_val_w = od_weights[:, 1:]
        od_val_w = od_val_w.astype(np.float)
        
        # weights ---> probability distributions for each row
        od_val_w = od_val_w/np.sum(od_val_w, axis=1)[:, None]
    
        for j in range(od_val_w.shape[0]):
            row_threshold_adjust = np.max(od_val_w[j, :]) / row_threshold
            od_val_w[j, od_val_w[j, :] < row_threshold_adjust] = 0
        
        od_val_sparse = coo_matrix(od_val_w)
        scipy.sparse.save_npz(os.path.basename(fi).split(".csv")[0] + ".npz", od_val_sparse)


def get_age_bucket(simulation_data):
    """
    Assign age bucket to an input population. These are the age buckets:
    0 - 15;
    16 - 19;
    20 - 24;
    25 - 29;
    30 - 44;
    45 - 59;
    60 - 74;
    75 +

    Parameters
    ----------
    simulation_data : Dataframe
        Input data from the VPH simulation

    Returns:
    -------
    A dataframe with a new column with the age bucket.

    """
    # Age buckets based on the file names 


    cut_bins = [-1, 16, 20, 25, 30, 45, 60, 75, 200]
    cut_labels = ["0to15", "16to19", "20to24", "25to29", "30to44", "45to59", "60to74", "75plus"]
    simulation_data.loc[:, "age_bucket"] = pd.cut(simulation_data['age'], bins=cut_bins, labels=cut_labels)

    return simulation_data