Create a small subset of real data for testing - 3 LADs per country and years up to 2029
test data is under source control - this script only required if the data format changes or you wish to manually
migrate to newly released data.

If you need to migrate to newly released data, you will need to download the full data into 
.ukpopulation/cache with an API Key specified in your environment. This can either be done by placing a file 
called NOMIS_API_KEY inside the download target dir that contains your personal API Key off nomisweb. There will 
be new file hashes for only the files starting with NM_200*_1_<hash>.py - since the data has changed. 
After you have downloaded the data into .ukpopulation/cache you should run the setup_test_data.py after changing the 
file names inside this script to point to the newly downloaded data - this will build smaller versions of the new 
data and place them into the tests/raw_data directory. 

Once this has been completed, you will then need to re-download the data using the DUMMY(which is contained in 
tests/raw_data/NOMIS_API_KEY) key directly into test/raw_data. Copy the hashes of those file names and overwrite the 
file names of the data setup by setup_test_data.py contained in raw data. This can be done either by running a 
unittest since which will attempt to download the data in raw_files in setup or run the methods inside this module. 

IMPORTANT: The way this change was handled is very convoluted and could be changed in future so that setting up the 
test data is handled using a setup script of some sort. When migrating, you will find that the tests may need some
editing in order for the code to be successfully tested. These are purely to make sure the code runs as intended and
results do not need to be strictly relevant.