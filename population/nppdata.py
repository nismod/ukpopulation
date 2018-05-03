
import numpy as np
import pandas as pd
#import requests
from openpyxl import load_workbook
import ukcensusapi.Nomisweb as Api
from bs4 import BeautifulSoup

def _read_excel_xml(path, sheet_name):
  file = open(path).read()
  soup = BeautifulSoup(file,'xml')
  worksheet = []
  for sheet in soup.findAll('Worksheet'): 
    if sheet["ss:Name"] == sheet_name:
      for row in sheet.findAll('Row'):
        row_as_list = []
        for cell in row.findAll('Cell'):
          data = cell.find('Data')
          if data:
              row_as_list.append(data.text)
        worksheet.append(row_as_list)
  return worksheet


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
    self.data = {}

    self.data["ppp"] = self.__download_ppp()

    #self.__download_variants()

  def __download_ppp(self):

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
    ppp = self.data_api.get_data(table_internal, query_params)
    # make age actual year
    ppp.C_AGE = ppp.C_AGE - 1
    # TODO merge 90+ for consistency with SNPP?

    return ppp
  
  def __download_variants(self):

    # TODO by country...(not Uk)

    variant = np.array(_read_excel_xml(self.cache_dir + "/uk_hpp_opendata2016.xml", "Population"))
    print(variant[0,:])
    print(variant[:,0])

    df = pd.DataFrame(data=variant[1:,0:], columns=variant[0,0:])
    #pd.DataFrame(data=males[1:,1:], index=males[1:,0], columns=males[0,1:])
    print(df.head())
#   Sex           Age    2016    2017    2018    2019    2020    2021    2022  \
# 0   1             0  401630  389769  403505  408285  412683  416741  420617
# 1   1             1  402554  404083  392142  405802  410510  414711  418678
# 2   1             2  406751  405885  407293  395271  408834  413295  417382
# 3   1             3  416855  409714  408734  410068  397968  411298  415658
# 4   1             4  430088  419536  412294  411246  412506  400183  413422

#      2023   ...      2107    2108    2109    2110    2111    2112    2113  \
# 0  421718   ...    508106  509490  510829  512100  513313  514466  515555
# 1  422467   ...    508705  510132  511516  512857  514130  515344  516497
# 2  421240   ...    509864  511324  512751  514134  515476  516749  517965
# 3  419646   ...    510674  512153  513614  515043  516424  517767  519040
# 4  417693   ...    511251  512728  514208  515668  517098  518478  519821

#      2114    2115    2116
# 0  516591  517569  518508
# 1  517588  518626  519605
# 2  519117  520208  521247
# 3  520255  521407  522500
# 4  521095  522310  523460