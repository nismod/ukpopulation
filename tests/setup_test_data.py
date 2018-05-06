#!/usr/bin/env python3

""" 
create a small subset of real data for testing - 3 LADs per country and years up to 2027
test data is under source control - this script only required if the data format changes
"""
import pandas as pd

real_data_dir = "./raw_data/"
test_data_dir = "./tests/raw_data/"

raw_files = ["NM_2006_1_56aba41fc0fab32f58ead6ae91a867b4.tsv", # England 
             "snpp_w.csv","snpp_s.csv","snpp_ni.csv"]


for file in raw_files:
  sep = "\t" if file[-4:] == ".tsv" else ","
  df = pd.read_csv(real_data_dir + file, sep=sep)

  geogs = df.GEOGRAPHY_CODE.unique()[:3]
  df = df[(df.GEOGRAPHY_CODE.isin(geogs)) & (df.PROJECTED_YEAR_NAME < 2028)]

  df.to_csv(test_data_dir + file, sep=sep, index=False)

# NB the file NM_2006_1_dbe6c087fb46306789f7d54b125482e4.tsv also needs to be in the test data folder,
# containing column headings only. (This will prevent the data being re-downloaded)