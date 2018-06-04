import matplotlib.pyplot as plt
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

years = range(snpp.min_year(), snpp.max_year())

variant = "hhh"
region = "E09000001"

npp.force_load_variants(npp.VARIANTS)
for k in npp.data:
  print("NPP ", k, ":", npp.data[k].C_AGE.unique())

print("SNPP:", snpp.data.C_AGE.unique())

for year in years:
  if year <= snpp.max_year():
  #age_sex = Utils.create_age_sex_marginal(self.snpp[self.snpp.PROJECTED_YEAR_NAME == year], self.region)
  # print(self.snpp[self.snpp.PROJECTED_YEAR_NAME == year])
  # print(self.snpp_api.create_variant(self.variant, self.npp_api, self.region, year))
    age_sex = snpp.create_variant(variant, npp, region, year)
  else:
    age_sex = snpp.extrapolate(npp, region, year)