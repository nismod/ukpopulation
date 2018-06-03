#!/usr/bin/env python3
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData

# TODO delete this file its superseded by the doc/example*.py  files

def main():
  npp = NPPData.NPPData()
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

  snpp = SNPPData.SNPPData()
  print(len(snpp.data))
  print(snpp.data.head())

  e = npp.year_ratio("ppp", ["en"], 2039, 2050)
  print(e)

  v = npp.variant_ratio("hhh", "en", range(2016,2039))
  print(v.head())

  print(snpp.extrapolate(npp, "E08000021", 2040))
  print(snpp.extrapolate(npp, "E08000021", 2100))


if __name__ == "__main__":
  main()
