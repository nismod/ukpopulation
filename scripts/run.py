#!/usr/bin/env python3
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData

def main():
  npp = NPPData.NPPData("./raw_data")
  #print(len(npp.data["ppp"]))
  #print(npp.data["ppp"].head())

  print(NPPData.NPPData.EW)

  data = npp.detail("lll", NPPData.NPPData.EW, range(2015,2051))

  print(data.GEOGRAPHY_CODE.unique())
  print(data.PROJECTED_YEAR_NAME.unique())
  print(data.C_AGE.unique())
  print(data.GENDER.unique())

  # sum over age and gender for each geography (and year)
  agg = npp.aggregate("GEOGRAPHY_CODE","lll", NPPData.NPPData.EW, range(2016,2051))
  print(agg)

  snpp = SNPPData.SNPPData("./raw_data")
  print(len(snpp.data))
  print(snpp.data.head())

  e = npp.year_ratio("ppp", ["en"], 2039, 2050)
  print(e)

  v = npp.variant_ratio("hhh", ["en"], range(2016,2039))
  print(v[v.PROJECTED_YEAR_NAME==2039])

  snpp.extrapolate(npp, "E08000021", 2040)
  snpp.extrapolate(npp, "E08000021", 2100)

  # plot population growth 
  ncle_act = snpp.aggregate("GEOGRAPHY_CODE", "E08000021", range(2016,2040))
  ncle_ext = snpp.extrapolagg("GEOGRAPHY_CODE", "E08000021", range(2040,2066)))
  ncle = ncle_act.append(ncle_ext)
  #matplotlib...

if __name__ == "__main__":
  main()
