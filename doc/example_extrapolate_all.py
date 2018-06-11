import pandas as pd
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# start with an empty data frame
result = pd.DataFrame()

country = utils.WA
horizon = 2050

# get the first year where extrapolation is necessary, extrapolate to 2050
ex_years = range(snpp.max_year(country) + 1, horizon + 1)


# loop over all the Welsh LADs 
for lad in snpp.data[country].GEOGRAPHY_CODE.unique():
  print(lad)

  # extrapolate and aggregate
  lad = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, ex_years)
  # append to data
  result = result.append(lad, ignore_index=True)

# write out results
result.to_csv("snpp_extrap_{}_{}.csv".format(country, horizon), index=False)

