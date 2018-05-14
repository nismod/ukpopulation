import pandas as pd
import population.nppdata as NPPData
import population.snppdata as SNPPData

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# get the first year where extrapolation is necessary
ex_start = snpp.max_year() + 1
# we extrapolate to 2050
ex_end = 2050 

# start with an empty data frame
result = pd.DataFrame()

# loop over all the UK LAD (or LAD-equivalents)
for lad in snpp.data.GEOGRAPHY_CODE.unique()[:5]:
  print(lad_ex)
  # extrapolate and aggregate
  lad_ex = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, range(ex_start, ex_end + 1))
  # append to data
  result = result.append(lad_ex, ignore_index=True)

# write out results
result.to_csv("snpp_extrap_2050.csv", index=False)

