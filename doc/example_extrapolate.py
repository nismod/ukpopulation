import matplotlib.pyplot as plt
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

lad = "E08000021" # Newcastle

# 50 year horizon
years = range(2016, 2067)

(in_years, ex_years) = utils.split_range(years, snpp.max_year())

# get the total projected population for pop up to the SNPP horizon (2039)
pop = snpp.aggregate(["GENDER", "C_AGE"], lad, in_years)
# extrapolate for another ~25 years
pop_ex = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, ex_years)

# plot the data
plt.plot(pop.PROJECTED_YEAR_NAME, pop.OBS_VALUE, "bo", label="SNPP")
plt.plot(pop_ex.PROJECTED_YEAR_NAME, pop_ex.OBS_VALUE, "b.", label="ext NPP")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.legend()
plt.title(lad + " Extrapolated Population (Principal Variant)")
plt.show()
