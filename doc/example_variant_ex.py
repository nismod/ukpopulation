import matplotlib.pyplot as plt
import population.nppdata as NPPData
import population.snppdata as SNPPData
import population.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

# 50 years, roughly half is extrapolated
years = range(2016, 2067)

# get the total projected (principal variant) population for newcastle, extrapolating as necessary
newcastle = snpp.extrapolagg(["GENDER", "C_AGE"], npp, "E08000021", years)

# calculate the the variants
newcastle_hhh = snpp.create_variant("hhh", npp, "E08000021", years)
newcastle_lll = snpp.create_variant("lll", npp, "E08000021", years)

# aggregate the calculated variants by age and gender
newcastle_hhh = utils.aggregate(newcastle_hhh, ["GENDER", "C_AGE"])
newcastle_lll = utils.aggregate(newcastle_lll, ["GENDER", "C_AGE"])

# plot the data
plt.plot(newcastle.PROJECTED_YEAR_NAME[:24], newcastle.OBS_VALUE[:24], "bo", label="ppp") 
plt.plot(newcastle.PROJECTED_YEAR_NAME[24:], newcastle.OBS_VALUE[24:], "b.", label="ppp (ext)") 
plt.plot(newcastle_hhh.PROJECTED_YEAR_NAME[:24], newcastle_hhh.OBS_VALUE[:24], "ro", label="hhh")
plt.plot(newcastle_hhh.PROJECTED_YEAR_NAME[24:], newcastle_hhh.OBS_VALUE[24:], "r.", label="hhh (ext)")
plt.plot(newcastle_lll.PROJECTED_YEAR_NAME[:24], newcastle_lll.OBS_VALUE[:24], "go", label="lll")
plt.plot(newcastle_lll.PROJECTED_YEAR_NAME[24:], newcastle_lll.OBS_VALUE[24:], "g.", label="lll (ext)")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title("Newcastle Extrapolated Population Projection Variants")
plt.legend()
plt.show()
