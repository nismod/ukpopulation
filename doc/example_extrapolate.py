import matplotlib.pyplot as plt
import population.nppdata as NPPData
import population.snppdata as SNPPData
import population.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# 50 year horizon
years = range(2016, 2067)

(in_years, ex_years) = utils.split_range(years, snpp.max_year())

# get the total projected population for newcastle up to the SNPP horizon (2039)
newcastle = snpp.aggregate(["GENDER", "C_AGE"], "E08000021", in_years)
# extrapolate for another ~25 years
newcastle_ex = snpp.extrapolagg(["GENDER", "C_AGE"], npp, "E08000021", ex_years)

# plot the data
plt.plot(newcastle.PROJECTED_YEAR_NAME, newcastle.OBS_VALUE, "bo", label="SNPP")
plt.plot(newcastle_ex.PROJECTED_YEAR_NAME, newcastle_ex.OBS_VALUE, "b.", label="ext NPP")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.legend()
plt.title("Newcastle Extrapolated Population (Principal Variant)")
plt.show()
