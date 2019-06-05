import numpy as np
import pandas as pd

import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils


snpp = SNPPData.SNPPData("./tests/raw_data")

lads = np.append(np.append(snpp.data[utils.EN].GEOGRAPHY_CODE.unique(), snpp.data[utils.WA].GEOGRAPHY_CODE.unique()), snpp.data[utils.SC].GEOGRAPHY_CODE.unique())
print(lads)

# custom = pd.read_csv("../simim/data/output/simim_production_ppp_scenario1.csv")
# print(len(custom.GEOGRAPHY_CODE.unique()))
# custom = custom[custom.GEOGRAPHY_CODE.isin(lads)]
# custom.loc[custom.GEOGRAPHY_CODE == "E06000005", "PEOPLE"] = custom[custom.GEOGRAPHY_CODE == "E06000005"].PEOPLE_ppp + 500
# custom.loc[custom.GEOGRAPHY_CODE == "E06000005", "net_delta"] = 500
# custom.to_csv("./tests/raw_data/test_scenario.csv", index=False)

custom = pd.read_csv("./tests/raw_data/test_scenario.csv")
# print(custom.GEOGRAPHY_CODE.dtype)
# print(custom.PROJECTED_YEAR_NAME.dtype)

print(max(custom.net_delta))
print(min(custom.net_delta))

snpp.data[utils.EN].PROJECTED_YEAR_NAME = snpp.data[utils.EN].PROJECTED_YEAR_NAME.astype(int)
cvar = snpp.custom_variant("./tests/raw_data/test_scenario.csv")
#cvar = snpp.custom_variant("../simim/data/output/simim_production_ppp_scenario1.csv")

print(cvar.GEOGRAPHY_CODE.unique())
print(cvar.PROJECTED_YEAR_NAME.unique())
print(len(cvar))