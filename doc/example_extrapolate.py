import matplotlib.pyplot as plt
import ukpopulation.myedata as MYEData
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
mye = MYEData.MYEData()
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

lad = "E07000041" # Exeter

# 50 year horizon
years = range(2011, 2067)

(mye_years, proj_years) = utils.split_range(years, mye.max_year())
(snpp_years, npp_years) = utils.split_range(proj_years, snpp.max_year(lad))

pop_mye = mye.aggregate(["GENDER", "C_AGE"], lad, mye_years)
# get the total projected population for pop up to the SNPP horizon (2039)
pop = snpp.aggregate(["GENDER", "C_AGE"], lad, snpp_years)
# extrapolate for another ~25 years
pop_ex = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, npp_years)

# plot the data
plt.plot(pop_mye.PROJECTED_YEAR_NAME, pop_mye.OBS_VALUE, "b^", label="MYE")
plt.plot(pop.PROJECTED_YEAR_NAME, pop.OBS_VALUE, "bo", label="SNPP")
plt.plot(pop_ex.PROJECTED_YEAR_NAME, pop_ex.OBS_VALUE, "b.", label="ext NPP")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.legend()
plt.title(lad + " Extrapolated Population (Principal Variant)")
plt.show()
