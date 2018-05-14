import sys
import os
import unittest
import numpy as np

#import ukcensusapi.Nomisweb as Api
import population.nppdata as NPPData
import population.snppdata as SNPPData

class Test(unittest.TestCase):

  def setUp(self):
    """ 
    Check env set up correctly for tests
    (it's too late to override the env in this function unfortunately)
    """
    if not os.environ["NOMIS_API_KEY"] == "DUMMY":
      print("Test requires NOMIS_API_KEY=DUMMY in env")
      sys.exit()

  def test_snpp(self):
    snpp = SNPPData.SNPPData("./tests/raw_data")    

    self.assertEqual(snpp.min_year(), 2014)
    self.assertEqual(snpp.max_year(), 2027) # for test data, real data is 2039

    # 12 LADs * 91 ages * 2 genders * 14 years
    self.assertEqual(len(snpp.data), 12 * 91 * 2 * 14)    

    #print(snpp.data.head())
    geogs = np.array(['E06000001', 'E06000005', 'E06000047', 'N09000001', 'N09000002', 'N09000011', 
                      'S12000033', 'S12000034', 'S12000041', 'W06000011', 'W06000016', 'W06000018'])
    self.assertTrue(np.array_equal(sorted(snpp.data.GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(snpp.data.PROJECTED_YEAR_NAME.unique()), np.array(range(2014,2028))))
    self.assertTrue(np.array_equal(sorted(snpp.data.C_AGE.unique()), np.array(range(0,91))))
    self.assertTrue(np.array_equal(snpp.data.GENDER.unique(), np.array([1,2])))

    data = snpp.filter(["E06000001","S12000041"], range(2016,2020))
    self.assertEqual(len(data), 1456) # 91(ages) * 2(genders) * 2(LADs) * 4(years)
    self.assertEqual(data[data.PROJECTED_YEAR_NAME==2016].OBS_VALUE.sum(), 209799) 

    agg = snpp.aggregate(["GENDER", "C_AGE"], ["E06000001","S12000041"], [2016])
    self.assertEqual(len(agg), 2)
    self.assertEqual(agg.OBS_VALUE.sum(), 209799) # remember this is population under 46

  def test_snpp_errors(self):
    snpp = SNPPData.SNPPData("./tests/raw_data")
    # invalid variant code
    #self.assertRaises(RuntimeError, snpp.filter, "xxx", NPPData.NPPData.UK, [2016])
    # invalid column name 
    self.assertRaises(ValueError, snpp.aggregate, ["INVALID_CAT"], ["E06000001","S12000041"], [2016])
    self.assertRaises(RuntimeError, snpp.aggregate, ["GENDER", "PROJECTED_YEAR_NAME"], ["E06000001","S12000041"], [2016])
    #invalid year? for now return empty
    self.assertEqual(len(snpp.filter(["E06000001","S12000041"], [2040])), 0)
    #self.assert

  def test_npp(self):
    npp = NPPData.NPPData("./tests/raw_data")    

    self.assertEqual(npp.min_year(), 2016)
    self.assertEqual(npp.max_year(), 2035) # for test data, real data is 2116

    # only ppp is present
    self.assertCountEqual(list(npp.data.keys()), ["ppp"])

    geogs = np.array(['E92000001', 'N92000002', 'S92000003', 'W92000004'])
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].PROJECTED_YEAR_NAME.unique()), np.array(range(2016,2036))))
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].C_AGE.unique()), np.array(range(0,45))))
    self.assertTrue(np.array_equal(npp.data["ppp"].GENDER.unique(), np.array([1,2])))

    # country populations for 2016 high variant
    data = npp.detail("hhh", NPPData.NPPData.EW, range(2016,2020))
    self.assertEqual(len(data), 736) # 46(ages) * 2(genders) * 2(countries) * 4(years)
    self.assertEqual(data[data.PROJECTED_YEAR_NAME==2016].OBS_VALUE.sum(), 33799230) 

    # now hhh and ppp are present
    self.assertCountEqual(list(npp.data.keys()), ["ppp", "hhh"])

    # similar to above, but all of UK summed by age and gender
    agg = npp.aggregate(["GENDER", "C_AGE"], "hhh", NPPData.NPPData.UK, [2016])
    self.assertEqual(len(agg), 4)
    self.assertEqual(agg.OBS_VALUE.sum(), 37906626) # remember this is population under 46

  def test_npp_errors(self):
    npp = NPPData.NPPData("./tests/raw_data")
    # invalid variant code
    self.assertRaises(RuntimeError, npp.detail, "xxx", NPPData.NPPData.UK, [2016])
    # invalid column name 
    #self.assertRaises(ValueError, npp.aggregate, ["WRONG_CODE", "GENDER"], "hhh", NPPData.NPPData.UK, [2016])
    self.assertRaises(RuntimeError, npp.aggregate, ["PROJECTED_YEAR_NAME"], "hhh", NPPData.NPPData.UK, [2016])
    #invalid year? for now return empty
    self.assertEqual(len(npp.detail("ppp", NPPData.NPPData.UK, [2015])), 0)
    #self.assert

  def test_snpp_extrapolate(self):
    pass

  def test_snpp_variant(self):
    pass 

if __name__ == "__main__":
  unittest.main()
