import os

# https://data.ngdc.noaa.gov/instruments/remote-sensing/passive/spectrometers-radiometers/imaging/viirs/dnb_composites
# /v10//201302/vcmcfg/SVDNB_npp_20130201-20130228_75N060E_vcmcfg_v10_c201605131247.tgz

month_list = ["01", "02", "03", "04", "05", "06",
              "07", "08", "09", "10", "11", "12"]

annual_list = ["2013", "2014", "2015", "2016", "2017"]

ntl_dataDir = "NTL"

web_prefix = "https://data.ngdc.noaa.gov/instruments/remote-sensing/passive/spectrometers-radiometers/imaging/viirs/dnb_composites/v10//"

for year in annual_list:
    for month in month_list:
        saveDir = os.path.join(ntl_dataDir, year, month)
        url = web_prefix + year + month + "/vcmcfg/"
        os.system("wget -r -l1 --no-parent --accept={0} {1}".format("SVDNB*_75N060E_*.tgz", url))

