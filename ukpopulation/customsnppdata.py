import glob
import os.path
import numpy as np
import pandas as pd
import ukpopulation.utils as utils

def _custom_snpp_filename(name, cache_dir):
  return os.path.join(cache_dir, "ukpopulation_custom_snpp_%s.csv" % name)

# save a custom projection in the cache dir
def register_custom_projection(name, data, cache_dir=utils.default_cache_dir()):

  # check data is compatible
  required_colnames = ["GEOGRAPHY_CODE", "OBS_VALUE", "GENDER","C_AGE","PROJECTED_YEAR_NAME"]
  for col in required_colnames:
    if not col in data.columns.values:
      raise ValueError("Custom SNPP dataset must contain a %s column" % col)

  if not (data.GENDER.unique() == [1, 2]).all():
    raise ValueError("GENDER column must only contain 1 (male) and 2 (female)")

  if min(data.C_AGE.unique()) != 0 or max(data.C_AGE.unique()) != 90:
    raise ValueError("C_AGE column must range from 0 to 90 (inclusive)")

  filename = _custom_snpp_filename(name, cache_dir)

  print("Writing custom SNPP %s to %s" % (name, filename))
  data.to_csv(filename, index=False)

def list_custom_projections(cache_dir=utils.default_cache_dir()):
  files = glob.glob(os.path.join(cache_dir, "ukpopulation_custom_snpp_*.csv"))
  projs = [os.path.basename(file)[25:-4] for file in files]
  return projs

class CustomSNPPData:
  """
  Functionality for cacheing and accessing custom Subnational Population Projection (NPP) data
  """
  def __init__(self, name, cache_dir=utils.default_cache_dir()):
    self.name = name
    self.cache_dir = cache_dir

    filename = _custom_snpp_filename(name, self.cache_dir)
    self.data = pd.read_csv(filename)

  def min_year(self, _=None):
    """
    Returns the first year in the projection
    (usused argument to make interface consistent with SNPPData)
    """
    # convert to country if necessary
    return min(self.data.PROJECTED_YEAR_NAME.unique())

  def max_year(self, _=None):
    """
    Returns the final year in the projection
    (usused argument to make interface consistent with SNPPData)
    """
    return max(self.data.PROJECTED_YEAR_NAME.unique())

  def all_lads(self):
    return self.data.GEOGRAPHY_CODE.unique()

  def filter(self, geog_codes, years=None, ages=range(0,91), genders=[1,2]):

    # convert inputs to arrays if single values supplied (for isin)
    if isinstance(geog_codes, str):
      geog_codes = [geog_codes]

    if years is None:
      years=range(self.min_year(), self.max_year()+1)
    if np.isscalar(years):
      years = [years]

    if np.isscalar(ages):
      ages = [ages]

    if np.isscalar(genders):
      genders = [genders]

    # check for any codes requested that werent present
    invalid_codes = np.setdiff1d(geog_codes, self.data.GEOGRAPHY_CODE.unique())
    if len(invalid_codes) > 0:
      raise ValueError("Filter for LAD code(s): %s for years %s returned no data (check also age/gender filters)" 
        % (str(invalid_codes), str(years)))

    # apply filters
    retval = self.data[(self.data.GEOGRAPHY_CODE.isin(geog_codes)) & 
                       (self.data.PROJECTED_YEAR_NAME.isin(years)) &
                       (self.data.C_AGE.isin(ages)) &
                       (self.data.GENDER.isin(genders))]

    return retval

  def aggregate(self, categories, geog_codes, years=None, ages=range(0,91), genders=[1,2]):

    data = self.filter(geog_codes, years, ages, genders)

    # invert categories (they're the ones to aggregate, not preserve)
    return data.groupby(utils.check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

  # year_range can include year that dont need to be extrapolated
  # Filtering age and gender is not (currently) supported
  def extrapolate(self, npp, geog_codes, year_range):

    if isinstance(geog_codes, str):
      geog_codes = [geog_codes]

    geog_codes = utils.split_by_country(geog_codes)

    all_codes_all_years = pd.DataFrame()

    for country in geog_codes:
      if not geog_codes[country]: continue

      maxyear = self.max_year()
      last_year = self.filter(geog_codes[country], maxyear)

      (in_range, ex_range) = utils.split_range(year_range, maxyear)
      # years that dont need to be extrapolated 
      all_years = self.filter(geog_codes[country], in_range) if in_range else pd.DataFrame()

      for year in ex_range:
        data = last_year.copy()
        scaling = npp.year_ratio("ppp", country, maxyear, year)
        data = data.merge(scaling[["GENDER", "C_AGE", "OBS_VALUE"]], on=["GENDER", "C_AGE"])
        data["OBS_VALUE"] = data.OBS_VALUE_x * data.OBS_VALUE_y
        data.PROJECTED_YEAR_NAME = year
        all_years = all_years.append(data.drop(["OBS_VALUE_x", "OBS_VALUE_y"], axis=1), ignore_index=True, sort=False)

      all_codes_all_years = all_codes_all_years.append(all_years, ignore_index=True, sort=False)
      
    return all_codes_all_years

  def extrapolagg(self, categories, npp, geog_codes, year_range):
    """
    Extrapolate and then aggregate
    """
    data = self.extrapolate(npp, geog_codes, year_range)

    # invert categories (they're the ones to aggregate, not preserve)
    return data.groupby(utils.check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

  def create_variant(self, variant_name, npp, geog_codes, year_range):
    """
    Apply NPP variant to SNPP: SNPP(v) = SNPP(0) * sum(a,g) [ NPP(v) / NPP(0) ]
    Preserves age-gender structure of SNPP data
    """  
    result = pd.DataFrame()
    if isinstance(geog_codes, str):
      geog_codes = [geog_codes]
    
    for geog_code in geog_codes:

      # split out any years prior to the NPP data (currently SNPP is 2014 based but NPP is 2016)
      (pre_range, in_range) = utils.split_range(year_range, npp.min_year() - 1)
      # for any years prior to NPP we just use the SNPP data as-is (i.e. "ppp")
      pre_data = self.filter(geog_code, pre_range) if pre_range else pd.DataFrame()
      if len(pre_data) > 0:
        print("WARNING: variant {} not applied for years {} that predate the NPP data".format(variant_name, pre_range))

      # return if there's nothing in the NPP range
      if not in_range:
        result.append(pre_data)
        continue

      data = self.extrapolate(npp, geog_code, in_range).sort_values(["C_AGE", "GENDER", "PROJECTED_YEAR_NAME"]).reset_index(drop=True)

      scaling = npp.variant_ratio(variant_name, utils.country(geog_code), year_range).reset_index().sort_values(["C_AGE", "GENDER", "PROJECTED_YEAR_NAME"])
      #scaling.to_csv(variant_name + ".csv", index=False)

      #print("DF: ", len(data), ":", len(scaling))
      assert(len(data) == len(scaling))
      data.OBS_VALUE = data.OBS_VALUE * scaling.OBS_VALUE
      
      # prepend any pre-NPP data
      result = result.append(pre_data.append(data))

    return result

