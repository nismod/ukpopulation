import sys
import os
import unittest
import numpy as np

#import ukcensusapi.Nomisweb as Api
import ukpopulation.myedata as MYEData
import ukpopulation.nppdata as NPPData
import ukpopulation.snppdata as SNPPData
import ukpopulation.snhpdata as SNHPData
import ukpopulation.utils as utils

class Test(unittest.TestCase):

  def setUp(self):
    """ 
    Check env set up correctly for tests
    (it's too late to override the env in this function unfortunately)
    """
    self.mye = MYEData.MYEData("./tests/raw_data")    
    self.npp = NPPData.NPPData("./tests/raw_data")    
    self.snpp = SNPPData.SNPPData("./tests/raw_data")    
    self.snhp = SNHPData.SNHPData("./tests/raw_data")

    # fix issue with test dataset
    self.snpp.data[utils.EN].PROJECTED_YEAR_NAME = self.snpp.data[utils.EN].PROJECTED_YEAR_NAME.astype(int)

    if not self.npp.data_api.key == "DUMMY" or not self.snpp.data_api.key == "DUMMY":
      print("Test requires NOMIS_API_KEY=DUMMY in env")
      sys.exit()

  def test_utils(self):
    year_range = range(2018,2050)
    (in_range, ex_range) = utils.split_range(year_range, self.snpp.max_year(utils.EN))
    self.assertEqual(min(in_range), min(year_range))
    self.assertEqual(max(in_range), 2027)
    self.assertEqual(min(ex_range), 2028)
    self.assertEqual(max(ex_range), max(year_range))

    self.assertEqual(utils.trim_range(2011, 1991, 2016), [2011])
    self.assertEqual(utils.trim_range(2011.0, 1991, 2016), [2011])
    self.assertEqual(utils.trim_range([2011], 1991, 2016), [2011])
    self.assertEqual(utils.trim_range([2011.0], 1991, 2016), [2011])
    self.assertEqual(utils.trim_range(np.array([1995,2005,2019]), 2001, 2011), [2005])
    self.assertEqual(utils.trim_range([1969,2111], 1991, 2016), [])
    self.assertEqual(utils.trim_range(range(1969,2111), 2011, 2016), list(range(2011,2017)))

    codes = "E09000001"
    self.assertTrue(utils.country(codes) == ["en"])
    codes = ['E06000002','E09000001']
    self.assertTrue(utils.country(codes) == ["en"])
    codes = ['E06000002','N09000001','S12000033','W06000011']
    self.assertTrue(utils.country(codes) == ['en', 'ni', 'sc', 'wa'])
    codes = ['E06000001','E06000002','N09000001','S12000033','W06000011']
    self.assertTrue(utils.country(codes) == ['en', 'ni', 'sc', 'wa'])
    codes = ['E06000001','W06000011','X06000002','Y09000001','Z12000033']
    self.assertTrue(utils.country(codes) == ["en", "wa"])
    codes = 'A06000001'
    self.assertTrue(utils.country(codes) == [])

    codes = ['E06000001','E06000002','N09000001','S12000033','W06000011']
    split = utils.split_by_country(codes)
    self.assertTrue(split[utils.EN] == ['E06000001','E06000002'])
    self.assertTrue(split[utils.WA] == ['W06000011'])
    self.assertTrue(split[utils.SC] == ['S12000033'])
    self.assertTrue(split[utils.NI] == ['N09000001'])

    # naively, each element would be rounded down, making the total 10
    fractional = np.array([0.1, 0.2, 0.3, 0.4]) * 11
    integral = utils.integerise(fractional)
    self.assertTrue(np.array_equal(integral, [1, 2, 3, 5]))

    # 1.51 is NOT increased because 4.5 has a larger fractional part when total is rescaled to 17 from 16.91
    fractional = np.array([1.1, 3.9, 4.5, 5.9, 1.51])
    integral = utils.integerise(fractional)
    self.assertTrue(np.array_equal(integral, [1, 4, 5, 6, 1]))

    # another example that preserves sum
    fractional = np.array([1.01] * 100)
    integral = utils.integerise(fractional)
    self.assertTrue(sum(integral) == 1.01 * 100)
    self.assertTrue(np.array_equal(np.unique(integral), [1, 2]))


  def test_mye(self):
    self.assertEqual(self.mye.min_year(), 1991)
    self.assertEqual(self.mye.max_year(), 2016) # for test data, real data is 2039

    year = 2011
    self.assertEqual(self.mye.aggregate(["GENDER", "C_AGE"], "E09000001", year).OBS_VALUE.sum(), 7412)
    self.assertEqual(self.mye.filter("E09000001", year).OBS_VALUE.sum(), 7412)

    self.assertEqual(self.mye.aggregate(["GENDER", "C_AGE"], "E09000001", year, genders=1).OBS_VALUE.sum(), 4133)
    self.assertEqual(self.mye.filter("E09000001", year, genders=1).OBS_VALUE.sum(), 4133)

    self.assertEqual(self.mye.aggregate(["GENDER", "C_AGE"], "E09000001", year, ages=range(16,75)).OBS_VALUE.sum(), 6333)
    self.assertEqual(self.mye.filter("E09000001", year, ages=range(16,75)).OBS_VALUE.sum(), 6333)

  def test_snpp(self):

    # NB this is the test data (real data is 2016-2041)
    self.assertEqual(self.snpp.min_year(utils.EN), 2014)
    self.assertEqual(self.snpp.max_year(utils.EN), 2027) # for test data, real data is 2039

    # test all_lads functionality
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.EN), ['E06000005', 'E06000047', 'E06000001']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.WA), ['W06000011', 'W06000016', 'W06000018']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.SC), ['S12000033', 'S12000034', 'S12000041']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.NI), ['N09000001', 'N09000011', 'N09000002']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.EW), 
      ['E06000005', 'E06000047', 'E06000001', 'W06000011', 'W06000016', 'W06000018']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.GB), 
      ['E06000005', 'E06000047', 'E06000001', 'W06000011', 'W06000016', 'W06000018', 'S12000033', 'S12000034', 'S12000041']))
    self.assertTrue(np.array_equal(self.snpp.all_lads(utils.UK), 
      ['E06000005', 'E06000047', 'E06000001', 'W06000011', 'W06000016', 'W06000018', 'S12000033', 'S12000034', 'S12000041', 'N09000001', 'N09000011', 'N09000002']))
    # North Korean projections are unavailable
    self.assertTrue(np.array_equal(self.snpp.all_lads("DPRK"), []))

    # 3 LADs * 91 ages * 2 genders * 14 years
    self.assertEqual(len(self.snpp.data[utils.EN]), 3 * 91 * 2 * 14)    

    #print(snpp.data.head())
    geogs = np.array(['E06000001', 'E06000005', 'E06000047', 'N09000001', 'N09000002', 'N09000011', 
                      'S12000033', 'S12000034', 'S12000041', 'W06000011', 'W06000016', 'W06000018'])
    self.assertTrue(np.array_equal(sorted(self.snpp.data[utils.EN].GEOGRAPHY_CODE.unique()), geogs[:3]))
    self.assertTrue(np.array_equal(sorted(self.snpp.data[utils.EN].PROJECTED_YEAR_NAME.unique()), np.array(range(2014,2028))))
    self.assertTrue(np.array_equal(sorted(self.snpp.data[utils.EN].C_AGE.unique()), np.array(range(0,91))))
    self.assertTrue(np.array_equal(self.snpp.data[utils.EN].GENDER.unique(), np.array([1,2])))

    data = self.snpp.filter(["E06000001","E06000005"], range(2016,2020))
    self.assertEqual(len(data), 1456) # 91(ages) * 2(genders) * 2(LADs) * 4(years)
    self.assertEqual(data[data.PROJECTED_YEAR_NAME==2016].OBS_VALUE.sum(), 198400) 

    agg = self.snpp.aggregate(["GENDER", "C_AGE"], ["S12000033","S12000041"], [2016])
    self.assertEqual(len(agg), 2)
    self.assertEqual(agg.OBS_VALUE.sum(), 349517) # remember this is population under 46

    # get from multiple countries at once
    codes = ['E06000001','N09000002','S12000033','W06000011']
    data = self.snpp.filter(codes, 2018)
    self.assertEqual(len(data), 728) # 91(ages) * 2(genders) * 4(LADs) * 1(years)
    self.assertEqual(sorted(data.GEOGRAPHY_CODE.unique()), codes) 

  def test_snpp_errors(self):
    # invalid variant code
    #self.assertRaises(RuntimeError, self.snpp.filter, "xxx", utils.UK, [2016])
    # invalid column name 
    self.assertRaises(ValueError, self.snpp.aggregate, ["INVALID_CAT"], ["E06000001","S12000041"], [2016])
    self.assertRaises(ValueError, self.snpp.aggregate, ["GENDER", "PROJECTED_YEAR_NAME"], ["E06000001","S12000041"], [2016])
    #invalid year
    self.assertRaises(ValueError, self.snpp.filter, ["E06000001","S12000041"], [2040])

    # check we get an error if an invalid LAD code is used
    self.assertRaises(ValueError, self.snpp.aggregate, ["GENDER", "C_AGE"], "E07000097", 2030)
  def test_npp(self):

    self.assertEqual(self.npp.min_year(), 2016)
    self.assertEqual(self.npp.max_year(), 2035) # for test data, real data is 2116

    # only ppp is present
    self.assertCountEqual(list(self.npp.data.keys()), ["ppp"])

    geogs = np.array(['E92000001', 'N92000002', 'S92000003', 'W92000004'])
    self.assertTrue(np.array_equal(sorted(self.npp.data["ppp"].GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(self.npp.data["ppp"].PROJECTED_YEAR_NAME.unique()), np.array(range(2016,2036))))
    self.assertTrue(np.array_equal(sorted(self.npp.data["ppp"].C_AGE.unique()), np.array(range(0,91))))
    self.assertTrue(np.array_equal(self.npp.data["ppp"].GENDER.unique(), np.array([1,2])))

    # country populations for 2016 high variant
    data = self.npp.detail("hhh", utils.EW, range(2016,2020))
    self.assertEqual(len(data), 1456) # 91(ages) * 2(genders) * 2(countries) * 4(years)
    self.assertEqual(data[data.PROJECTED_YEAR_NAME==2016].OBS_VALUE.sum(), 58381217) 

    # now hhh and ppp are present
    self.assertCountEqual(list(self.npp.data.keys()), ["ppp", "hhh"])

    # similar to above, but all of UK summed by age and gender
    agg = self.npp.aggregate(["GENDER", "C_AGE"], "hhh", utils.UK, [2016])
    self.assertEqual(len(agg), 4)
    self.assertEqual(agg.OBS_VALUE.sum(), 65648054) # remember this is population under 46

  def test_npp_errors(self):
    # invalid variant code
    self.assertRaises(RuntimeError, self.npp.detail, "xxx", utils.UK, [2016])
    # invalid column name 
    #self.assertRaises(ValueError, self.npp.aggregate, ["WRONG_CODE", "GENDER"], "hhh", utils.UK, [2016])
    self.assertRaises(ValueError, self.npp.aggregate, ["PROJECTED_YEAR_NAME"], "hhh", utils.UK, [2016])
    #invalid year? for now return empty
    self.assertEqual(len(self.npp.detail("ppp", utils.UK, [2015])), 0)
    #self.assert

  def test_snpp_extrapolate(self):
    # test extrapolation within range just returns the data
    years = range(self.snpp.min_year(utils.EN), self.snpp.min_year(utils.EN) + 2)
    ext = self.snpp.extrapolate(self.npp, "E06000001", years)
    act = self.snpp.filter("E06000001", years)
    self.assertTrue(ext.equals(act))

    # test extrapolagg is equivalent to extrapolate + external agg
    years = range(self.snpp.max_year(utils.EN)-1, self.snpp.max_year(utils.EN) + 2)
    ext = utils.aggregate(self.snpp.extrapolate(self.npp, "E06000001", years), ["GENDER", "C_AGE"])
    extagg = self.snpp.extrapolagg(["GENDER", "C_AGE"], self.npp, "E06000001", years)
    self.assertTrue(ext.equals(extagg))

    # test works for multiple LADs
    extagg = self.snpp.extrapolagg(["GENDER", "C_AGE"], self.npp, ["E06000001", "E06000005", "E06000047", "S12000033", "S12000041"], years)
    self.assertTrue(np.array_equal(extagg.PROJECTED_YEAR_NAME.unique(), years))
    self.assertTrue(np.array_equal(extagg.GEOGRAPHY_CODE.unique(), ["E06000001", "E06000005", "E06000047", "S12000033", "S12000041"]))

    # check for non-contiguous extrapolation-only range
    years = [2030,2035]
    extagg = self.snpp.extrapolagg(["GENDER", "C_AGE"], self.npp, ["E06000001", "E06000005", "E06000047", "S12000033", "S12000041"], years)
    self.assertTrue(np.array_equal(extagg.PROJECTED_YEAR_NAME.unique(), years))
    self.assertTrue(np.array_equal(extagg.GEOGRAPHY_CODE.unique(), ["E06000001", "E06000005", "E06000047", "S12000033", "S12000041"]))

  def test_snpp_variant(self):
    # test variant projection 
    years = range(self.snpp.min_year(utils.EN) , self.snpp.min_year(utils.EN) + 3)

    # most of this just tests the code runs without error
    base = self.snpp.filter("E06000001", years).sort_values(["PROJECTED_YEAR_NAME", "GENDER", "C_AGE"])
    # this should be identical to above
    ppp = self.snpp.create_variant("ppp", self.npp, "E06000001", years).sort_values(["PROJECTED_YEAR_NAME", "GENDER", "C_AGE"])
    hhh = self.snpp.create_variant("hhh", self.npp, "E06000001", years)
    lll = self.snpp.create_variant("lll", self.npp, "E06000001", years)

    # TODO more testing of results
    self.assertTrue(np.array_equal(base.OBS_VALUE, ppp.OBS_VALUE))

  def test_snpp_custom_variant(self):
    custom = self.snpp.custom_variant("./tests/raw_data/test_scenario.csv")

    self.assertTrue(np.array_equal(custom.GEOGRAPHY_CODE.unique(), ['E06000005', 'E06000047', 'E06000001', 'S12000033', 'S12000034', 'S12000041', 'W06000011', 'W06000016', 'W06000018']))
    self.assertTrue(np.array_equal(custom.PROJECTED_YEAR_NAME.unique(), [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027]))
    self.assertTrue(len(custom), 9 * 12 * 2 * 91) # 9 geogs, 12 years, 2 genders, 91 ages = 19656

  # test datasets have consistent ranges
  def test_consistency(self):
    self.npp.force_load_variants(["hhh", "ppp", "lll"])

    snpp_ages = self.snpp.data[utils.EN].C_AGE.unique()
    snpp_genders = self.snpp.data[utils.EN].GENDER.unique()
    for k in self.npp.data:
      self.assertTrue(np.array_equal(snpp_ages, self.npp.data[k].C_AGE.unique()))
      self.assertTrue(np.array_equal(snpp_genders, self.npp.data[k].GENDER.unique()))

  def test_snhp_errors(self):
    # invalid variant code
    self.assertRaises(IndexError, self.snhp.aggregate, "Q01234567", [2016])


  def test_snhp(self):
    self.assertEqual(self.snhp.min_year(utils.EN), 2011)    
    self.assertEqual(self.snhp.max_year(utils.EN), 2041)    
    self.assertEqual(self.snhp.min_year(utils.WA), 2014)    
    self.assertEqual(self.snhp.max_year(utils.WA), 2039)    
    self.assertEqual(self.snhp.min_year(utils.SC), 2016)    
    self.assertEqual(self.snhp.max_year(utils.SC), 2041)    
    self.assertEqual(self.snhp.min_year(utils.NI), 2016)    
    self.assertEqual(self.snhp.max_year(utils.NI), 2041)    

    data=self.snhp.aggregate(["E06000001", "W06000023", "S12000033", "N09000001"], [2016])
    self.assertEqual(len(data), 4)
    print(data)
    self.assertEqual(data.PROJECTED_YEAR_NAME.unique(), 2016)
    self.assertEqual(data.iloc[0].GEOGRAPHY_CODE, "E06000001")
    self.assertAlmostEqual(data.iloc[0].OBS_VALUE, 41220.456)
    self.assertEqual(data.iloc[1].GEOGRAPHY_CODE, "N09000001")
    self.assertAlmostEqual(data.iloc[1].OBS_VALUE, 55155.0)
    self.assertEqual(data.iloc[2].GEOGRAPHY_CODE, "S12000033")
    self.assertAlmostEqual(data.iloc[2].OBS_VALUE, 106748.0)
    self.assertEqual(data.iloc[3].GEOGRAPHY_CODE, "W06000023")
    self.assertAlmostEqual(data.iloc[3].OBS_VALUE, 59255.35, delta=0.001)

  # # Try to recreate problems in microsimulation
  # def test_integration(self):

  #   years = range(self.snpp.min_year(), self.snpp.max_year())
    
  #   variant = "hhh"
  #   region = "E06000001"

  #   for year in years:
  #     if year <= self.snpp.max_year():
  #     #age_sex = Utils.create_age_sex_marginal(self.snpp[self.snpp.PROJECTED_YEAR_NAME == year], self.region)
  #     # print(self.snpp[self.snpp.PROJECTED_YEAR_NAME == year])
  #     # print(self.snpp_api.create_variant(self.variant, self.npp_api, self.region, year))
  #       age_sex = self.snpp.create_variant(variant, self.npp, region, year)
  #       print(len(age_sex))
  #     else:
  #       age_sex = self.snpp.extrapolate(self.npp, region, year)
  #   self.assertTrue(False)

if __name__ == "__main__":
  unittest.main()
