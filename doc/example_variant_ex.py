import matplotlib.pyplot as plt
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# 50 years, roughly half is extrapolated
years = range(2016, 2067)

lad = "E08000021" # Newcastle

# get the total projected (principal variant) population for ppp, extrapolating as necessary
ppp = snpp.extrapolagg(["GENDER", "C_AGE"], npp, lad, years)

# calculate the the variants
hhh = snpp.create_variant("hhh", npp, lad, years)
lll = snpp.create_variant("lll", npp, lad, years)

# aggregate the calculated variants by age and gender
hhh = utils.aggregate(hhh, ["GENDER", "C_AGE"])
lll = utils.aggregate(lll, ["GENDER", "C_AGE"])

# plot the data
plt.plot(ppp.PROJECTED_YEAR_NAME[:24], ppp.OBS_VALUE[:24], "bo", label="ppp") 
plt.plot(ppp.PROJECTED_YEAR_NAME[24:], ppp.OBS_VALUE[24:], "b.", label="ppp (ext)") 
plt.plot(hhh.PROJECTED_YEAR_NAME[:24], hhh.OBS_VALUE[:24], "ro", label="hhh")
plt.plot(hhh.PROJECTED_YEAR_NAME[24:], hhh.OBS_VALUE[24:], "r.", label="hhh (ext)")
plt.plot(lll.PROJECTED_YEAR_NAME[:24], lll.OBS_VALUE[:24], "go", label="lll")
plt.plot(lll.PROJECTED_YEAR_NAME[24:], lll.OBS_VALUE[24:], "g.", label="lll (ext)")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title(lad + " Extrapolated Population Projection Variants")
plt.legend()
plt.show()
