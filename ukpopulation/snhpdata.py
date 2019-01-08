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
    self.data[utils.WA] = self.__do_wales()
    self.data[utils.SC] = self.__do_scotland()
    #self.data[utils.NI] = self.__do_nireland()


  def __do_wales(self):
    print("Collating SNHP data for Wales...")

    wales_raw = self.cache_dir + "/snhp_w.csv"
    if os.path.isfile(wales_raw): 
      snpp_w = pd.read_csv(wales_raw)
    else:
      fields = ['Area_AltCode1','Year_Code','Data','Area_Hierarchy','Variant_Code','Householdtype_ItemName_ENG']
      # StatsWales is an OData endpoint, so select fields of interest
      url = "http://open.statswales.gov.wales/dataset/hous0115?$select={}".format(",".join(fields))
      # use OData syntax to filter P (persons), AllAges (all ages), Area_Hierarchy 596 (LADs)
      url += "&$filter=Variant_Code eq 1 and Area_Hierarchy eq 'W92000004'" #Householdtype_ItemName_ENG
      data = []
      while True:
        print(url)
        r = requests.get(url)
        r.raise_for_status()
        r_data = r.json()
        data += r_data['value']
        if "odata.nextLink" in r_data:
          url = r_data["odata.nextLink"]
        else:
          break
      snpp_w = pd.DataFrame(data)

      # # Remove unwanted and rename wanted columns
      snpp_w = snpp_w.drop(["Area_Hierarchy", "Variant_Code"], axis=1)
      snpp_w = snpp_w.rename(columns={"Area_AltCode1": "GEOGRAPHY_CODE",
                                      "Data": "OBS_VALUE", 
                                      "Householdtype_ItemName_ENG": "HOUSEHOLD_TYPE",
                                      "Year_Code": "PROJECTED_YEAR_NAME"})
      snpp_w.HOUSEHOLD_TYPE.replace("Households", "All", inplace=True)

      # Drop occupancy and population (for now, might be useful?)
      snpp_w = snpp_w[~snpp_w.HOUSEHOLD_TYPE.isin(["Projected Private Household Population", "Average Household Size"])]
      snpp_w.to_csv(wales_raw, index=False)

    return snpp_w



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

      chunk = pd.read_csv(z.open(filename, "r"), encoding="latin1", skiprows=3, skipfooter=) \
        .dropna(how="all") \
        .drop(["Unnamed: 28", "Unnamed: 29", "Unnamed: 30"], axis=1) \
        .replace(",", "", regex=True) 
      #print(chunk)
      chunk = chunk[chunk["Unnamed: 1"] != "All ages"].drop("Unnamed: 1", axis=1)
      chunk.fillna(method='ffill', inplace=True)
      chunk = chunk[chunk["Unnamed: 0"].isin(["1 adult: male", "1 adult: female", "1 adult, 1+ children", "2 adults", "2+ adults, 1+ children", "3+ adults", "All households"])]
      chunk = pd.melt(chunk, id_vars="Unnamed: 0")
      chunk.value = chunk.value.astype(int)
      chunk = chunk.groupby(["Unnamed: 0", "variable"]).sum().reset_index().rename({"Unnamed: 0": "HOUSEHOLD_TYPE", "variable": "PROJECTED_YEAR_NAME", "value": "OBS_VALUE"}, axis=1)
      chunk.insert(0, "GEOGRAPHY_CODE", lookup[lookup.LAD_NAME == council_area].LAD.values[0])
      snhp_s = snhp_s.append(chunk, ignore_index=True)

    return snhp_s


    