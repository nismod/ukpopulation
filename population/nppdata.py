
import os.path
import requests
import zipfile
import time
import numpy as np
import pandas as pd
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

    # TODO use 
    variants = ["hhh"]#, "lll"]

    datasets = {
      "en": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z3zippedpopulationprojectionsdatafilesengland/2016based/tablez3opendata16england.zip",
      "wa": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z4zippedpopulationprojectionsdatafileswales/2016based/tablez4opendata16wales.zip",
      "sc": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z5zippedpopulationprojectionsdatafilesscotland/2016based/tablez5opendata16scotland.zip",
      "ni": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z6zippedpopulationprojectionsdatafilesnorthernireland/2016based/tablez6opendata16northernireland.zip",
    }

    codes = {
      "en": "E92000001",
      "wa": "W92000004",
      "sc": "S92000003",
      "ni": "N92000002"
    }

    for variant in variants: 
      dataset = self.cache_dir + "/npp_" + variant + ".csv"
      if not os.path.isfile(dataset):
        pass 
      self.data[variant] = pd.DataFrame()

    # download, unzip collate and reformat data if not presentcd
    for country in ["en"]: #datasets:
      raw_zip = self.cache_dir + "/npp_" + country + ".zip"
      if not os.path.isfile(raw_zip): 
        response = requests.get(datasets[country])
        with open(raw_zip, 'wb') as fd:
          for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)   
      z = zipfile.ZipFile(raw_zip)

      #variants = z.namelist() 
      for vname in variants:
        print(vname)
        vxml = country + "_" + vname + "_opendata2016.xml"
        #vcsv = self.cache_dir + "/" + country + "_" + vname + "_opendata2016.csv"
        if not os.path.isfile(self.cache_dir + "/" + vxml):
          z.extract(vname, path=self.cache_dir)
        start = time.time()
        variant = np.array(_read_excel_xml(self.cache_dir + "/" + vxml, "Population"))
        print("read xml in " + str(time.time() - start))
        #df = pd.DataFrame(data=variant[1:,2:], columns=variant[0,2:], index=variant[1:,:2])
        df = pd.DataFrame(data=variant[1:,0:], columns=variant[0,0:])
        df = df.set_index(["Sex", "Age"]).stack().reset_index()
        # remove padding
        df.Age = df.Age.str.strip()
        df.columns = ["GENDER", "C_AGE", "PROJECTED_YEAR_NAME", "OBS_VALUE"]
        #print(df.head())

        # list age categories we are aggregating
        a = ["90", "91", "92", "93", "94", "95", "96", "97", "98", "99", "100", "101", "102", "103", "104", "105 - 109", "110 and over"]

        # copy the data in these categories
        dfagg = df[df.C_AGE.isin(a)]
        print(dfagg.head())

        # The aggregration goes haywire unless the data is saved and reloaded - comment out lines below to see
        # TODO this needs to be fixed and/or reported as a (reproducible) bug
        tmpfile = "./tmp.csv"
        dfagg.to_csv(tmpfile, index=False)
        dfagg = pd.read_csv(tmpfile)

        dfagg = dfagg.groupby(["GENDER", "PROJECTED_YEAR_NAME"])["OBS_VALUE"].sum().reset_index()
        dfagg["C_AGE"] = "90"
        print(dfagg.head())

        # print(df.head())
        # print(dfagg.head())
        # print(df.columns)
        # print(dfagg.columns)
        # remove the aggregated categories from the original and append the aggregate
        df = df[~df.C_AGE.isin(a)].append(dfagg, ignore_index=True)
 
        # add the country code
        df["GEOGRAPHY_CODE"] = codes[country]

        #df.to_csv(vcsv, index=None)
        self.data[vname] = self.data[vname].append(df, ignore_index=True)
    
    for variant in variants: 
      filename = self.cache_dir + "/npp_" + variant + ".csv"
      self.data[variant].to_csv(filename, index=None)


      # snpp_s = pd.DataFrame()
      # for year in range(2014,2040):
      #   for gender in [1,2]:
      #     filename = "Population-"+str(year)+("-Male" if gender==1 else "-Female")+".csv"
      #     chunk = pd.read_csv(z.open(filename)    

    # print(variant[0,:])
    # print(variant[:,0])

    # df = pd.DataFrame(data=variant[1:,0:], columns=variant[0,0:])
    # #pd.DataFrame(data=males[1:,1:], index=males[1:,0], columns=males[0,1:])

    # df.to_csv(self.cache_dir + "/uk_hpp_opendata2016.csv",index=None)
    # print(df.head())


# file = "raw_data/en_pph_opendata2016.xml.csv"
# #df = pd.DataFrame(data=variant[1:,2:], columns=variant[0,2:], index=variant[0:,:2])
# df = pd.read_csv(file).set_index(keys=["Sex","Age"])
# s = df.stack().reset_index()
# s.columns=["GENDER", "C_AGE", "PROJECTED_YEAR_NAME", "OBS_VALUE"]
# s["GEOGRAPHY_CODE"] = "K000"

