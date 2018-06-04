import matplotlib.pyplot as plt
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

start_year = 2016
end_year = snpp.max_year()

# get the total projected population for newcastle up to the SNPP horizon (2039)
newcastle = snpp.aggregate(["GENDER", "C_AGE"], "E08000021", range(start_year, end_year + 1))

# calculate the the variants
newcastle_hhh = snpp.create_variant("hhh", npp, "E08000021", range(start_year, end_year + 1))
newcastle_lll = snpp.create_variant("lll", npp, "E08000021", range(start_year, end_year + 1))

# aggregate the calculated variants by age and gender
newcastle_hhh = utils.aggregate(newcastle_hhh, ["GENDER", "C_AGE"])
newcastle_lll = utils.aggregate(newcastle_lll, ["GENDER", "C_AGE"])

# plot the data
plt.plot(newcastle.PROJECTED_YEAR_NAME, newcastle.OBS_VALUE, "bo", label="ppp") 
plt.plot(newcastle_hhh.PROJECTED_YEAR_NAME, newcastle_hhh.OBS_VALUE, "ro", label="hhh")
plt.plot(newcastle_lll.PROJECTED_YEAR_NAME, newcastle_lll.OBS_VALUE, "go", label="lll")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title("Newcastle Population Projection Variants")
plt.legend()
plt.show()
