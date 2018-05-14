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