"""
Common utility functions for NPP/SNPP
"""

import os 
import numpy as np
from pathlib import Path

# Country enumerations
EN = "en"
WA = "wa"
SC = "sc"
NI = "ni"

# Aggregations
EW = [EN, WA]
GB = [EN, WA, SC]
UK = [EN, WA, SC, NI]

# ONS country codes
CODES = {
  EN: "E92000001",
  WA: "W92000004",
  SC: "S92000003",
  NI: "N92000002"
}

def country(codes):
  """ 
  Returns country from ONS LAD code or 2-letter country code (above) - simply looks at first letter, case insensitive
  """
  if isinstance(codes, str):
    codes=[codes]
  lookup={"E": EN, "W": WA, "S": SC, "N": NI}
  #return lookup[code[0].upper()]
  raw = set([code[0] in lookup and lookup[code[0]] for code in codes])
  raw.discard(False)
  return sorted(list(raw))
  #set([code[0] in lookup and lookup[code[0]].upper() for code in codes]).discard(False))

def split_by_country(codes):
  """
  Splits a single array of LAD codes into separate arrays for each country 
  """
  return { EN: [code for code in codes if code.startswith("E")],
           WA: [code for code in codes if code.startswith("W")],
           SC: [code for code in codes if code.startswith("S")],
           NI: [code for code in codes if code.startswith("N")] }

def default_cache_dir():
  """
  Default cache dir location, ensures the path exists (failing if it cannot create) 
  This *should* work on all platforms
  """
  cache_dir = str(Path.home() / ".ukpopulation/cache")
  
  if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
  return cache_dir

def check_and_invert(categories):
  """
  Takes a list of categories to aggregrate and removes them from all possible categories, 
  creating a list of categories to preserve that can be used by groupby
  Will thow ValueError if one of supplied categories is not one of the column names below
  """
  inverted = ['C_AGE', 'GENDER', 'GEOGRAPHY_CODE', 'PROJECTED_YEAR_NAME']
  # first ensure list
  if isinstance(categories, str):
    categories = [categories]

  if "PROJECTED_YEAR_NAME" in categories:
    raise ValueError("It makes no sense to aggregate data over PROJECTED_YEAR_NAME")

  for cat in categories:
    inverted.remove(cat)

  return inverted

def filter_by_age(data, age_range):
  return data[data.C_AGE.isin(age_range)]

def aggregate(detail, categories):
  """
  Aggregate OBS_VALUE over categories
  """
  return detail.groupby(check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

def split_range(full_range, cutoff):
  """
  Split a range of values into those within (<=) cutoff and those without (>)
  Returns a tuple containing 2 lists (which can be empty)
  """
  if np.isscalar(full_range):
    full_range = [full_range]

  return ([x for x in full_range if x <= cutoff], [x for x in full_range if x > cutoff])

def trim_range(input_range, minval, maxval):
  """
  Removes values < minval or > maxval from input_range
  If input_range is None, defaults to the inclusive range: range(minval, maxval + 1) 
  """
  if input_range is None:
    return range(minval, maxval + 1)
  
  if np.isscalar(input_range):
    input_range = [input_range]

  return [x for x in input_range if x >= minval and x <= maxval]

def read_cell_range(worksheet, topleft, bottomright):
  data_rows = []
  for row in worksheet[topleft:bottomright]:
    data_cols = []
    for cell in row:
      data_cols.append(cell.value)
    data_rows.append(data_cols)
  return np.array(data_rows)

def integerise(series):
  """
  This duplicates functionality that exists in humanleague, rather than intorducing a package dependency solely for this function
  """
  sumf = sum(series)
  sumi = round(sumf)
  # rescale series to nearest-integer sum
  series = series * sumi / sumf
  # get integer and fractional parts
  seriesi = np.floor(series)
  seriesf = series - seriesi
  # shortfall is integer sum less sum of integer values
  shortfall = int(sumi - sum(seriesi))
  # select the n largest fractional parts where n=shortfall 
  idx = np.argpartition(seriesf, -shortfall)[-shortfall:]
  #increment the values at these indices
  inc = np.zeros(len(series))
  np.put(inc, idx, 1)
  return seriesi + inc
