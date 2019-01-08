"""
snhpdata.py - household projections
"""
import os.path
import zipfile
import pandas as pd
import requests
import ukpopulation.utils as utils

class SNHPData:
  """
  Functionality for downloading and collating UK Subnational Household Projection (SNHP) data
  """  

  def __init__(self, cache_dir=None):
    if cache_dir is None:
      cache_dir = utils.default_cache_dir()
    self.cache_dir = cache_dir
    #self.data_api = Api.Nomisweb(self.cache_dir) 

    self.data = {}
    #self.data[utils.EN] = self.__do_england()
    #self.data[utils.WA] = self.__do_wales()
    self.data[utils.SC] = self.__do_scotland()
    #self.data[utils.NI] = self.__do_nireland()


  def __do_scotland(self):
    print("Collating SNHP data for Scotland...")

    #scotland_raw = self.cache_dir + "/snhp_s.csv"
    scotland_src = "https://www.nrscotland.gov.uk/files//statistics/household-projections/16/2016-house-proj-detailed-coun-princ.zip"
    scotland_zip = os.path.join(self.cache_dir, "2016-house-proj-detailed-coun-princ.zip")

    if not os.path.isfile(scotland_zip): 
      response = requests.get(scotland_src)
      with open(scotland_zip, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=1024):
          fd.write(chunk)
        print("Downloaded", scotland_zip)

    lookup = pd.read_csv("../microsimulation/persistent_data/gb_geog_lookup.csv.gz")
    z = zipfile.ZipFile(scotland_zip)

    snhp_s = pd.DataFrame()
    for filename in z.namelist():
      council_area = filename[36:-4].strip()
      #print(">%s<" % council_area)
      if council_area == "Na h-Eileanan Siar":
        council_area = "Comhairle nan Eilean Siar"
      elif council_area == "Scotland":
        continue

      chunk = pd.read_csv(z.open(filename, "r"), encoding="latin1", skiprows=3) \
        .drop(["Unnamed: 1", "Unnamed: 28", "Unnamed: 29", "Unnamed: 30"], axis=1) \
        .replace(",", "", regex=True) 
      lad = chunk[chunk["Unnamed: 0"] == "All households"].drop("Unnamed: 0", axis=1).astype(int)
      lad.insert(0, "GEOGRAPHY_CODE", lookup[lookup.LAD_NAME == council_area].LAD.values[0])
      snhp_s = snhp_s.append(lad, ignore_index=True)

    return snhp_s