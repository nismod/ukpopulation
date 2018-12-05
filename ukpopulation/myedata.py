"""
MYEData - wrapper around Mid-Year Estimate data by LAD, SYoA and gender
"""

import pandas as pd
import ukcensusapi.Nomisweb as Api
import ukpopulation.utils as utils

class MYEData:
  """
  Functionality for downloading and collating UK mid-year estimate (MYE) data
  Nomisweb stores the data for the entire UK, from 1991-2016 inclusive
  """  

  # update as and when necessary (this is unlike (S)NPP where we query the data for the year range)
  # the data is stored differently at nomisweb (year is part of the query) 
  MIN_YEAR = 1991
  MAX_YEAR = 2016

  def __init__(self, cache_dir=None):
    if cache_dir is None:
      cache_dir = utils.default_cache_dir()
    self.cache_dir = cache_dir
    self.data_api = Api.Nomisweb(self.cache_dir) 

    # store as a dictionary keyed by year (lazy retrieval)
    self.data = {}

  def min_year(self):
    """
    Returns the first year in the data
    """
    return MYEData.MIN_YEAR

  def max_year(self):
    """
    Returns the final year in the data
    """
    return MYEData.MAX_YEAR

  # TODO functionality for easy aggregration to E/W/EW/S/GB/NI/UK

  def filter(self, geog_codes, years=None, ages=range(0,91), genders=[1,2]):
    """
    Get MYE detailed data for a given year
    """
    # ensure array inputs
    if isinstance(geog_codes, str):
      geog_codes = [geog_codes]
    if isinstance(ages, int):
      ages = [ages]
    if isinstance(genders, int):
      genders = [genders]

    result = pd.DataFrame()

    years = utils.trim_range(years, self.min_year(), self.max_year())

    for year in years:

      # ensure the data is loaded
      self.__fetch_data(year)

      ## ensure we return a copy!
      part = self.data[year][(self.data[year].GEOGRAPHY_CODE.isin(geog_codes)) &
                             (self.data[year].C_AGE.isin(ages)) &
                             (self.data[year].GENDER.isin(genders))].copy()
      part["PROJECTED_YEAR_NAME"] = year
      result = result.append(part)

    return result.reset_index(drop=True)

  def aggregate(self, categories, geog_codes, years=None, ages=range(0,91), genders=[1,2]):

    data = self.filter(geog_codes, years, ages, genders)

    # invert categories (they're the ones to aggregate, not preserve)
    return data.groupby(utils.check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

  def __fetch_data(self, year):
    """
    Gets Mid-year population estimate data for a given year
    Data is by single year of age by gender by local authority
    """
    # if data already loaded return 
    if year in self.data:
      return

    table_internal = "NM_2002_1" # 2016-based MYE
    query_params = {
      "gender": "1,2",
      "c_age": "101...191",
      "MEASURES": "20100",
      "select": "geography_code,gender,c_age,obs_value",
      "geography": "1879048193...1879048573,1879048583,1879048574...1879048582"
    }

    if year < MYEData.MIN_YEAR or year > MYEData.MAX_YEAR:
      raise ValueError("{} is outside the available years for MYE data ({}-{})".format(year, MIN_YEAR, MAX_YEAR))

    query_params["date"] = "latest"
    if year < MYEData.MAX_YEAR:
      query_params["date"] += "MINUS" + str(2016-year)

    self.data[year] = self.data_api.get_data(table_internal, query_params)

    # renumber age so that 0 means [0,1)
    self.data[year].C_AGE -= 101

    return self.data[year]

