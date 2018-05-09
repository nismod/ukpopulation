import sys
import os
import unittest
import numpy as np

#import ukcensusapi.Nomisweb as Api
import population.nppdata as NPPData
import population.snppdata as SNPPData

class Test(unittest.TestCase):

  # def __init__(self, *args, **kwargs):
  #   super(Test, self).__init__(*args, **kwargs)

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

    # 12 LADs * 91 ages * 2 genders * 14 years
    self.assertEqual(len(snpp.data), 12 * 91 * 2 * 14)    

    #print(snpp.data.head())
    geogs = np.array(['E06000001', 'E06000005', 'E06000047', 'N09000001', 'N09000002', 'N09000011', 
                      'S12000033', 'S12000034', 'S12000041', 'W06000011', 'W06000016', 'W06000018'])
    self.assertTrue(np.array_equal(sorted(snpp.data.GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(snpp.data.PROJECTED_YEAR_NAME.unique()), np.array(range(2014,2028))))
    self.assertTrue(np.array_equal(sorted(snpp.data.C_AGE.unique()), np.array(range(0,91))))
    self.assertTrue(np.array_equal(snpp.data.GENDER.unique(), np.array([1,2])))

  def test_npp(self):
    npp = NPPData.NPPData("./tests/raw_data")    
    # only ppp is present
    self.assertListEqual(list(npp.data.keys()), ["ppp"])

    geogs = np.array(['E92000001', 'N92000002', 'S92000003', 'W92000004'])
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].PROJECTED_YEAR_NAME.unique()), np.array(range(2016,2036))))
    self.assertTrue(np.array_equal(sorted(npp.data["ppp"].C_AGE.unique()), np.array(range(0,45))))
    self.assertTrue(np.array_equal(npp.data["ppp"].GENDER.unique(), np.array([1,2])))

    data = npp.detail("hhh", NPPData.NPPData.EW, range(2016,2020))
    
    # country populations for 2016 high variant
    agg = npp.aggregate(["GEOGRAPHY_CODE", "PROJECTED_YEAR_NAME"], "hhh", NPPData.NPPData.UK, [2016])
    self.assertEqual(len(agg), 4)
    self.assertEqual(agg.OBS_VALUE.sum(), 37906626) # remember this is population under 46

if __name__ == "__main__":
  unittest.main()
