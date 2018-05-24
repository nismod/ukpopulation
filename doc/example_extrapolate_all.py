import pandas as pd
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# get the first year where extrapolation is necessary, extrapolate to 2050
ex_years = range(snpp.max_year() + 1, 2051)

# start with an empty data frame
result = pd.DataFrame()

# loop over all the UK LAD (or LAD-equivalents)
for lad in snpp.data.GEOGRAPHY_CODE.unique()[:5]:
  print(lad)
  # extrapolate and aggregate
  lad = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, ex_years)
  # append to data
  result = result.append(lad, ignore_index=True)

# write out results
result.to_csv("snpp_extrap_2050.csv", index=False)

