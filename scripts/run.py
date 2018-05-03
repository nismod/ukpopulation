#!/usr/bin/env python3
import population.nppdata as NPPData
import population.snppdata as SNPPData

def main():
  nppdata = NPPData.NPPData("./raw_data")
  snppdata = SNPPData.SNPPData("./raw_data")
  
if __name__ == "__main__":
  main()
