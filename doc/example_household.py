import matplotlib.pyplot as plt
import ukpopulation.snppdata as SNPPData
import ukpopulation.snhpdata as SNHPData
#import ukpopulation.utils as utils

# initialise the population modules
snhp = SNHPData.SNHPData()
snpp = SNPPData.SNPPData()

lad = "E08000021" # Newcastle

start_year = 2016
end_year = snhp.max_year(lad)
# get the total 
hh = snhp.aggregate(lad, range(start_year, end_year + 1))
p = snpp.aggregate(["C_AGE", "GENDER"], lad, range(start_year, end_year + 1)) 

# plot the data
fig, ax1 = plt.subplots()
ax1.plot(hh.PROJECTED_YEAR_NAME, hh.OBS_VALUE, "bo", label="households") 
ax1.set_xlabel("Year")
ax1.set_ylabel("Households")
ax1.legend()
ax2 = ax1.twinx()
ax2.plot(p.PROJECTED_YEAR_NAME, p.OBS_VALUE, "ro", label="people") 
ax2.set_xlabel("Year")
ax2.set_ylabel("People")
ax2.legend(loc=4)

plt.title(lad + " Households/People Projections")
plt.show()

