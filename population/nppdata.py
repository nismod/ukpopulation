
import os.path
import numpy as np
import pandas as pd
import requests
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

  VARIANTS = {
    "hhh": "High population", 
    "hpp": "High fertility",
    "lll": "Low population",
    "lpp": "Low fertility",
    "php": "High life expectancy",
    "pjp": "",
    "pkp": "",
    "plp": "Low life expectancy",
    "pph": "High migration",
    "ppl": "Low migration",
    "ppp": "Principal",
    "ppq": "",
    "ppr": "",
    "pps": "",
    "ppz": "Zero net migration"
  }

# Young age structure 	hlh 				
# Old age structure 	lhl 				
# Replacement fertility 	rpp 				
# Constant fertility 	cpp 				
# No mortality improvement 	pnp 				
# No change 	cnp 				
# Long term balanced net migration 	ppb 	

  def __init__(self, cache_dir = "./raw_data"):
    self.cache_dir = cache_dir
    self.data_api = Api.Nomisweb(self.cache_dir) 
    # map of pandas dataframes keyed by variant code
    self.data = {}

    self.data["ppp"] = self.__download_ppp()

    self.__download_variants()

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

    datasets = {
      "e":  "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z3zippedpopulationprojectionsdatafilesengland/2016based/tablez3opendata16england.zip",
      "w":  "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z4zippedpopulationprojectionsdatafileswales/2016based/tablez4opendata16wales.zip",
      "s":  "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z5zippedpopulationprojectionsdatafilesscotland/2016based/tablez5opendata16scotland.zip",
      "ni": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z6zippedpopulationprojectionsdatafilesnorthernireland/2016based/tablez6opendata16northernireland.zip",
    }

    for key in datasets:
      raw_zip = self.cache_dir + "/npp_" + key + ".zip"
      if not os.path.isfile(raw_zip): 
        response = requests.get(datasets[key])
        with open(raw_zip, 'wb') as fd:
          for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)

    # variant = np.array(_read_excel_xml(self.cache_dir + "/uk_hpp_opendata2016.xml", "Population"))
    # print(variant[0,:])
    # print(variant[:,0])

    # df = pd.DataFrame(data=variant[1:,0:], columns=variant[0,0:])
    # #pd.DataFrame(data=males[1:,1:], index=males[1:,0], columns=males[0,1:])

    # df.to_csv(self.cache_dir + "/uk_hpp_opendata2016.csv",index=None)
    # print(df.head())



