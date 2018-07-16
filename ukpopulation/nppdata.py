
import os.path
import requests
import zipfile
import time
import numpy as np
import pandas as pd
from openpyxl import load_workbook
import ukcensusapi.Nomisweb as Api
from bs4 import BeautifulSoup
import ukpopulation.utils as utils

def _read_excel_xml(path, sheet_name):
  file = open(path, encoding="utf8")
  soup = BeautifulSoup(file, 'xml')
  worksheet = []
  for sheet in soup.find_all('Worksheet'):
    # workaround for an intermittent issue where the "ss:" prefix disappears from the attribute keys
    # Probably related to this xml namespace issue: 
    # https://stackoverflow.com/questions/37195992/beautifulsoup4-removes-namespace-definitions-from-schema-in-wsdl
    if sheet.get("ss:Name") == sheet_name or sheet.get("Name") == sheet_name:
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

  def __init__(self, cache_dir = None):
    if cache_dir is None:
      cache_dir = utils.default_cache_dir()
    self.cache_dir = cache_dir
    self.data_api = Api.Nomisweb(self.cache_dir) 
    # map of pandas dataframes keyed by variant code
    self.data = {}

    # load principal aggressively...
    self.data["ppp"] = self.__download_ppp()

    # ...and variants lazily
    #self.__download_variants()

  def min_year(self):
    """
    Returns the first year in the projection
    """
    return min(self.data["ppp"].PROJECTED_YEAR_NAME.unique())

  def max_year(self):
    """
    Returns the final year in the projection
    """
    return max(self.data["ppp"].PROJECTED_YEAR_NAME.unique())


  def detail(self, variant_name, geog, years=None, ages=range(0,91), genders=[1,2]):
    """
    Return a subset of the raw data
    """
    if not variant_name in NPPData.VARIANTS:
      raise RuntimeError("invalid variant name: " + variant_name)
    # make years a valid range (this *silently* removes invalid years)
    years = utils.trim_range(years, self.min_year(), self.max_year())

    if not variant_name in self.data:
      # is it a standard variant
      if variant_name in NPPData.VARIANTS:
        self.__load_variant(variant_name)
      else:
        raise RuntimeError("Invalid variant name / custom variants are not yet implemented")

    # apply filters
    if isinstance(geog, str):
      geog = [geog]
    geog_codes = [utils.CODES[g] for g in geog]
    return self.data[variant_name][(self.data[variant_name].GEOGRAPHY_CODE.isin(geog_codes)) & 
                                   (self.data[variant_name].PROJECTED_YEAR_NAME.isin(years)) &
                                   (self.data[variant_name].C_AGE.isin(ages)) &
                                   (self.data[variant_name].GENDER.isin(genders))].reset_index(drop=True)


  def aggregate(self, categories, variant_name, geog, years=None, ages=range(0,91), genders=[1,2]):
    """
    Subset and aggregate the raw data
    """

    data = self.detail(variant_name, geog, years, ages, genders)

    return data.groupby(utils.check_and_invert(categories))["OBS_VALUE"].sum().reset_index()

  def year_ratio(self, variant_name, geog, ref_year, year, ages=range(0,91), genders=[1,2]):
    """
    Ratio to ref_year projection for selected geog/years/ages/genders 
    """
    # TODO do we need to (re)index these to ensure the piecewise mult is correct?
    ref = self.detail(variant_name, geog, [ref_year], ages, genders)
    num = self.detail(variant_name, geog, [year], ages, genders)

    assert(len(ref) == len(num))
    num.OBS_VALUE = num.OBS_VALUE / ref.OBS_VALUE
    return num

  def variant_ratio(self, variant_numerator, geog, years, ages=range(0,91), genders=[1,2]): 
    """
    Ratio to principal projection for selected geog/years/ages/genders 
    """
    # this function only works for a single country (which is ok)
    ref = self.detail("ppp", geog, years, ages, genders).set_index(["C_AGE", "GENDER", "PROJECTED_YEAR_NAME"])

    num = self.detail(variant_numerator, geog, years, ages, genders).set_index(["C_AGE", "GENDER", "PROJECTED_YEAR_NAME"])

    assert(len(ref) == len(num))
    num.OBS_VALUE = num.OBS_VALUE / ref.OBS_VALUE
    #print(num.query("GENDER==2 and C_AGE==6 and PROJECTED_YEAR_NAME==2018"))

    # return multiindexed df
    return num

  def force_load_variants(self, variants):

    for variant in variants:
      if not variant in self.data:
        self.__load_variant(variant)
    return 

  def __download_ppp(self):

    print("Loading NPP principal (ppp) data for England, Wales, Scotland & Northern Ireland")

    table_internal = "NM_2009_1" # 2016-based NPP (principal)
    query_params = {
      "gender": "1,2",
      "c_age": "1...106",
      "MEASURES": "20100",
      "date": "latest",
      "projected_year": "2016...2116",
      "select": "geography_code,projected_year_name,gender,c_age,obs_value",
      "geography": "2092957699...2092957702"
    }
    ppp = self.data_api.get_data(table_internal, query_params)
    # make age actual year
    ppp.C_AGE = ppp.C_AGE - 1
    # TODO merge 90+ for consistency with SNPP
    pop90plus = ppp[ppp.C_AGE >= 90].groupby(["GENDER", "PROJECTED_YEAR_NAME", "GEOGRAPHY_CODE"])["OBS_VALUE"].sum().reset_index()
    pop90plus["C_AGE"] = 90

    # remove the aggregated categories from the original and append the aggregate
    ppp = ppp[ppp.C_AGE < 90].append(pop90plus, ignore_index=True, sort=False)

    return ppp
  
  def __load_variant(self, variant_name):

    # [4 country zips] -> [60 xml] -> [60 raw csv] -> [15 variant csv]

    datasets = {
      utils.EN: "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z3zippedpopulationprojectionsdatafilesengland/2016based/tablez3opendata16england.zip",
      utils.WA: "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z4zippedpopulationprojectionsdatafileswales/2016based/tablez4opendata16wales.zip",
      utils.SC: "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z5zippedpopulationprojectionsdatafilesscotland/2016based/tablez5opendata16scotland.zip",
      utils.NI: "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationprojections/datasets/z6zippedpopulationprojectionsdatafilesnorthernireland/2016based/tablez6opendata16northernireland.zip",
    }

    # check for cached data
    dataset = self.cache_dir + "/npp_" + variant_name + ".csv"
    if not os.path.isfile(dataset):
      # assemble data if not already cached
      self.data[variant_name] = pd.DataFrame()

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
        print("Extracting " + country + "_" + variant_name)
        vxml = country + "_" + variant_name + "_opendata2016.xml"
        if not os.path.isfile(self.cache_dir + "/" + vxml):
          z.extract(vxml, path=self.cache_dir)
        start = time.time()
        vdata = np.array(_read_excel_xml(str(self.cache_dir + "/" + vxml), "Population"))
        print("read xml in " + str(time.time() - start))
        df = pd.DataFrame(data=vdata[1:,0:], columns=vdata[0,0:])
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
        df["GEOGRAPHY_CODE"] = utils.CODES[country]

        #df.to_csv(vcsv, index=None)
        self.data[variant_name] = self.data[variant_name].append(df, ignore_index=True)
      
      # step 3: save preprocessed data
      self.data[variant_name].to_csv(dataset, index=None)

    self.data[variant_name] = pd.read_csv(dataset)
