import matplotlib.pyplot as plt
import population.nppdata as NPPData
import population.snppdata as SNPPData

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# get the first year where extrapolation is necessary
ex_start = snpp.max_year() + 1

# get the total projected population for newcastle up to the SNPP horizon (2039)
newcastle = snpp.aggregate(["GENDER", "C_AGE"], "E08000021", range(2018, ex_start))
# extrapolate for another 25 years
newcastle_ex = snpp.extrapolagg(["GENDER", "C_AGE"], npp, "E08000021", range(ex_start, ex_start + 25))

# plot the data
plt.plot(newcastle.PROJECTED_YEAR_NAME, newcastle.OBS_VALUE, "bo", newcastle_ex.PROJECTED_YEAR_NAME, newcastle_ex.OBS_VALUE, "ro")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title("Newcastle Population Projection (red=extrapolated NPP)")
plt.show()
