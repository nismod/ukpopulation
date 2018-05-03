
import pandas as pd
#import requests
#from openpyxl import load_workbook
import ukcensusapi.Nomisweb as Api

class NPPData:
  """
  Functionality for downloading and collating UK National Population Projection (NPP) data, including variants
  Nomisweb stores the UK principal variant (only)
  Other variants are avilable online in zipped xml files
  """
  def __init__(self, cache_dir = "./raw_data"):
    self.cache_dir = cache_dir
    self.data_api = Api.Nomisweb(self.cache_dir) 
    # map of pandas dataframes keyed by variant code
    self.npp = {}

    table_internal = "NM_2009_1" # 2016-based NPP (principal)
    query_params = {
      "gender": "1,2",
      "c_age": "1...105",
      "MEASURES": "20100",
      "date": "latest",
      "projected_year": "2016...2116",
      "select": "geography_code,projected_year_name,gender,c_age,obs_value",
      "geography": "2092957699...2092957702"
    }
    self.npp["ppp"] = self.data_api.get_data(table_internal, query_params)
    # make age actual year
    self.npp["ppp"].C_AGE = self.npp["ppp"].C_AGE - 1
    # TODO merge 90+ for consistency with SNPP?

    print(self.npp["ppp"].head())
  #def __

