import matplotlib.pyplot as plt
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

lad = "E08000021" # Newcastle

start_year = 2016
end_year = snpp.max_year(lad)


# get the total projected population for ppp up to the SNPP horizon (2039)
ppp = snpp.aggregate(["GENDER", "C_AGE"], lad, range(start_year, end_year + 1))

# calculate the the variants
hhh = snpp.create_variant("hhh", npp, lad, range(start_year, end_year + 1))
lll = snpp.create_variant("lll", npp, lad, range(start_year, end_year + 1))

# aggregate the calculated variants by age and gender
hhh = utils.aggregate(hhh, ["GENDER", "C_AGE"])
lll = utils.aggregate(lll, ["GENDER", "C_AGE"])

# plot the data
plt.plot(ppp.PROJECTED_YEAR_NAME, ppp.OBS_VALUE, "bo", label="ppp") 
plt.plot(hhh.PROJECTED_YEAR_NAME, hhh.OBS_VALUE, "ro", label="hhh")
plt.plot(lll.PROJECTED_YEAR_NAME, lll.OBS_VALUE, "go", label="lll")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title(lad + " Population Projection Variants")
plt.legend()
plt.show()
