#!/usr/bin/env python3
import population.nppdata as NPPData
import population.snppdata as SNPPData

def main():
  npp = NPPData.NPPData("./raw_data")
  #print(len(npp.data["ppp"]))
  #print(npp.data["ppp"].head())

  print(NPPData.NPPData.EW)

  data = npp.get_npp("hhh", NPPData.NPPData.EW, range(2016,2051))

  print(data.GEOGRAPHY_CODE.unique())
  print(data.PROJECTED_YEAR_NAME.unique())
  print(data.C_AGE.unique())
  print(data.GENDER.unique())

  # sum over age and gender
  agg = npp.aggregate(data, "GEOGRAPHY_CODE")
  print(agg)

  snpp = SNPPData.SNPPData("./raw_data")
  print(len(snpp.data))
  print(snpp.data.head())

if __name__ == "__main__":
  main()
