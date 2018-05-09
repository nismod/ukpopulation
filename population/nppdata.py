
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
  CODES = {
    "en": "E92000001",
    "wa": "W92000004",
    "sc": "S92000003",
    "ni": "N92000002"
  }
  EW = ["en", "wa"]
  GB = ["en", "wa", "sc"]
  UK = ["en", "wa", "sc", "ni"]


  VARIANTS = {
    "hhh": "High population", 
    "hpp": "High fertility",
    "lll": "Low population",
    "lpp": "Low fertility",
    "php": "High life expectancy",
    "pjp": "Moderately high life expectancy",
    "pkp": "Moderately low life expectancy",
    "plp": "Low life expectancy",
    "pph": "High migration",
    "ppl": "Low migration",
    "ppp": "Principal",
    "ppq": "0% future EU migration (non-ONS)",
    "ppr": "50% future EU migration (non-ONS)",
    "pps": "150% future EU migration (non-ONS)",
    "ppz": "Zero net migration"
  }
  # Other variants not in data?
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

    # load principal aggressively...
    self.data["ppp"] = self.__download_ppp()

    # ...and variants lazily
    #self.__download_variants()

  def detail(self, variant_name, geog, years, ages=range(0,91), genders=[1,2]):
    if not variant_name in NPPData.VARIANTS:
      raise RuntimeError("invalid variant name: " + variant_name)
    file = self.cache_dir + "/npp_" + variant_name + ".csv"
    if not os.path.isfile(file):
      self.__download_variants()
    data = pd.read_csv(file)

    # apply filters
    geog_codes = [NPPData.CODES[g] for g in geog]
    return data[(data.GEOGRAPHY_CODE.isin(geog_codes)) & 
                (data.PROJECTED_YEAR_NAME.isin(years)) &
                (data.C_AGE.isin(ages)) &
                (data.GENDER.isin(genders))].reset_index()


  def aggregate(self, categories, variant_name, geog, years, ages=range(0,91), genders=[1,2]):

    data = self.detail(variant_name, geog, years, ages, genders)

    # ensure list
    if isinstance(categories, str):
      categories = [categories]
    if not "PROJECTED_YEAR_NAME" in categories:
      print("Not aggregating over PROJECTED_YEAR_NAME as it makes no sense")
      categories.append("PROJECTED_YEAR_NAME")
    return data.groupby(categories)["OBS_VALUE"].sum().reset_index()

  def year_ratio(self, variant_name, geog, ref_year, year, ages=range(0,91), genders=[1,2]):
    """
    Ratio to ref_year projection for selected geog/years/ages/genders 
    """
    ref = self.detail(variant_name, geog, [ref_year], ages, genders)
    num = self.detail(variant_name, geog, [year], ages, genders)

    num.OBS_VALUE = num.OBS_VALUE / ref.OBS_VALUE
    return num

  def variant_ratio(self, variant_numerator, geog, years, ages=range(0,91), genders=[1,2]): 
    """
    Ratio to principal projection for selected geog/years/ages/genders 
    """
    pass

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

    # [4 country zips] -> [60 xml] -> [60 raw csv] -> [15 variant csv]

    datasets = {
      "en": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z3zippedpopulationprojectionsdatafilesengland/2016based/tablez3opendata16england.zip",
      "wa": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z4zippedpopulationprojectionsdatafileswales/2016based/tablez4opendata16wales.zip",
      "sc": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z5zippedpopulationprojectionsdatafilesscotland/2016based/tablez5opendata16scotland.zip",
      "ni": "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z6zippedpopulationprojectionsdatafilesnorthernireland/2016based/tablez6opendata16northernireland.zip",
    }

    for variant in NPPData.VARIANTS: 
      dataset = self.cache_dir + "/npp_" + variant + ".csv"
      if not os.path.isfile(dataset):
        pass 
      self.data[variant] = pd.DataFrame()

    # step 1: download, country-level zip file containing all variants (if not already there)
    for country in datasets:
      raw_zip = self.cache_dir + "/npp_" + country + ".zip"
      if not os.path.isfile(raw_zip): 
        print("downloading " + raw_zip)
        response = requests.get(datasets[country])
        with open(raw_zip, 'wb') as fd:
          for chunk in response.iter_content(chunk_size=1024):
            fd.write(chunk)   
      else:
        print("using " + raw_zip)


    for country in datasets:
      raw_zip = self.cache_dir + "/npp_" + country + ".zip"
      z = zipfile.ZipFile(raw_zip)
      # step 2: unzip, collate and reformat data if not presentcd
      #variants = z.namelist() 
      for vname in NPPData.VARIANTS:
        print(country + "_" + vname)
        vxml = country + "_" + vname + "_opendata2016.xml"
        #vcsv = self.cache_dir + "/" + country + "_" + vname + "_opendata2016.csv"
        if not os.path.isfile(self.cache_dir + "/" + vxml):
          z.extract(vxml, path=self.cache_dir)
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
        #print(dfagg.head())

        # The aggregration goes haywire unless the data is saved and reloaded - comment out lines below to see
        # TODO this needs to be fixed and/or reported as a (reproducible) bug
        tmpfile = self.cache_dir + "/tmp.csv"
        dfagg.to_csv(tmpfile, index=False)
        dfagg = pd.read_csv(tmpfile)

        dfagg = dfagg.groupby(["GENDER", "PROJECTED_YEAR_NAME"])["OBS_VALUE"].sum().reset_index()
        dfagg["C_AGE"] = "90"
        #print(dfagg.head())

        # print(df.head())
        # print(dfagg.head())
        # print(df.columns)
        # print(dfagg.columns)
        # remove the aggregated categories from the original and append the aggregate
        df = df[~df.C_AGE.isin(a)].append(dfagg, ignore_index=True)
 
        # add the country code
        df["GEOGRAPHY_CODE"] = NPPData.CODES[country]

        #df.to_csv(vcsv, index=None)
        self.data[vname] = self.data[vname].append(df, ignore_index=True)
    
    # step 3: save preprocessed data
    for variant in NPPData.VARIANTS: 
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

