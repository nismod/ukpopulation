"""
Common utility functions for NPP/SNPP
"""

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
    raise RuntimeError("It makes no sense to aggregate data over PROJECTED_YEAR_NAME")

  for cat in categories:
    inverted.remove(cat)

  return inverted

def aggregate(detail, categories):
  """
  Aggregate OBS_VALUE over categories
  """
  return detail.groupby(check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

def split_range(full_range, cutoff):
  """
  Split a year range into those within (incl) cutoff and those without
  """
  return ([x for x in full_range if x <= cutoff], [x for x in full_range if x > cutoff])
