
import os
import unittest
import numpy as np

#import ukcensusapi.Nomisweb as Api
import population.nppdata as NPPData
import population.snppdata as SNPPData

class Test(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(Test, self).__init__(*args, **kwargs)

  def test__env(self):
    """ 
    Ensure environmnet set up correctly for tests
    """
    self.assertEqual(os.environ["NOMIS_API_KEY"], "DUMMY")

  def test_snpp(self):
    snpp = SNPPData.SNPPData("./tests/raw_data")    

    # 12 LADs * 91 ages * 2 genders * 14 years
    self.assertEqual(len(snpp.data), 12 * 91 * 2 * 14)    

    #print(snpp.data.head())
    print(sorted(snpp.data.GEOGRAPHY_CODE.unique()))
    geogs = np.array(['E06000001', 'E06000005', 'E06000047', 'N09000001', 'N09000002', 'N09000011', 
                      'S12000033', 'S12000034', 'S12000041', 'W06000011', 'W06000016', 'W06000018'])
    self.assertTrue(np.array_equal(sorted(snpp.data.GEOGRAPHY_CODE.unique()), geogs))
    self.assertTrue(np.array_equal(sorted(snpp.data.PROJECTED_YEAR_NAME.unique()), np.array(range(2014,2028))))
    self.assertTrue(np.array_equal(sorted(snpp.data.C_AGE.unique()), np.array(range(0,91))))
    self.assertTrue(np.array_equal(snpp.data.GENDER.unique(), np.array([1,2])))
    
if __name__ == "__main__":
  unittest.main()
