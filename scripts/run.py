#!/usr/bin/env python3
import population.nppdata as NPPData
import population.snppdata as SNPPData

def main():
  npp = NPPData.NPPData("./raw_data")
  print(len(npp.data["ppp"]))
  print(npp.data["ppp"].head())

  snpp = SNPPData.SNPPData("./raw_data")
  print(len(snpp.data))
  print(snpp.data.head())


if __name__ == "__main__":
  main()
