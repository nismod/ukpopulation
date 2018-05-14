import matplotlib.pyplot as plt
import population.nppdata as NPPData
import population.snppdata as SNPPData
import population.utils as utils

# initialise the population modules
npp = NPPData.NPPData()
snpp = SNPPData.SNPPData()

start_year = 2016
end_year = 2039 #snpp.max_year()

# get the total projected population for newcastle up to the SNPP horizon (2039)
newcastle = snpp.aggregate(["GENDER", "C_AGE"], "E08000021", range(start_year, end_year + 1))
# approximate variants

# def create_variant(self, variant_name, npp, geog_code, year_range):

# scaling = npp.variant_ratio("hhh", ["en"], range(2016, 2039))
# scaling1 = scaling[(scaling.C_AGE==1) & (scaling.GENDER==1)]
# scaling10 = scaling[(scaling.C_AGE==10) & (scaling.GENDER==1)]
# plt.plot(scaling1.PROJECTED_YEAR_NAME, scaling1.OBS_VALUE, "bo", scaling10.PROJECTED_YEAR_NAME, scaling10.OBS_VALUE, "go") 
# plt.show()

#newcastle     = snpp.create_variant("ppp", npp, "E08000021", range(2016, end_year + 1))#, ["GENDER", "C_AGE"])
newcastle_hhh = snpp.create_variant("hhh", npp, "E08000021", range(start_year, end_year + 1))#, ["GENDER", "C_AGE"])
newcastle_lll = snpp.create_variant("lll", npp, "E08000021", range(start_year, end_year + 1))#, ["GENDER", "C_AGE"])

newcastle_hhh = utils.aggregate(newcastle_hhh, ["GENDER", "C_AGE"])
newcastle_lll = utils.aggregate(newcastle_lll, ["GENDER", "C_AGE"])

print(newcastle.head())
print(newcastle_hhh.head())
print(newcastle_lll.head())

# print(len(newcastle))
# print(len(newcastle_hhh))
# print(len(newcastle_lll))

# plot the data
plt.plot(
  newcastle.PROJECTED_YEAR_NAME, newcastle.OBS_VALUE, "bo", 
  newcastle_hhh.PROJECTED_YEAR_NAME, newcastle_hhh.OBS_VALUE, "ro",
  newcastle_lll.PROJECTED_YEAR_NAME, newcastle_lll.OBS_VALUE, "go")
plt.xlabel("Year")
plt.ylabel("Persons")
plt.title("Newcastle Population Projections")
plt.show()
