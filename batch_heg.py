# -*- coding: utf-8 -*-
import os

# 设置HEG相关环境变量
os.environ['MRTDATADIR']='/Users/lyy/Downloads/OuterLIB/hegMACv2.15.Build9.8/heg/data'
os.environ['PGSHOME']='/Users/lyy/Downloads/OuterLIB/hegMACv2.15.Build9.8/heg/TOOLKIT_MTD'
os.environ['MRTBINDIR']='/Users/lyy/Downloads/OuterLIB/hegMACv2.15.Build9.8/heg/bin'

hegpath = '/Users/lyy/Downloads/OuterLIB/hegMACv2.15.Build9.8/heg/bin'
hegdo = os.path.join(hegpath, 'resample')

inpath = "/Users/lyy/Downloads/MODIS/raw_data"
outpath = "/Users/lyy/Downloads/MODIS/tiff_data"
prmpath = "/Users/lyy/Downloads/MODIS/prm_data"

allfiles = os.listdir(inpath)
allhdffiles = [f for f in allfiles if f.endswith(".hdf")]

corner_dict = {"h26v04": ["( 49.999999996 104.432583132 )", "( 39.999999996 140.015144392 )"],
               "h26v05": ["( 39.999999996 92.37604306 )", "( 29.999999997 117.486656023 )"],
               "h27v04": ["( 49.999999996 117.486656023 )", "( 39.999999996 155.572382658 )"],
               "h27v05": ["( 39.999999996 103.923048442 )", "( 29.999999997 130.540728915 )"]}

for eachhdf in allhdffiles:
    NDVI_date = eachhdf.split(".")[1]
    corner = corner_dict[eachhdf.split(".")[2]]
    prm=['NUM_RUNS = 1\n',
      'BEGIN\n',
      'INPUT_FILENAME = ' + inpath +'/'+ eachhdf +'\n',
      'OBJECT_NAME = MOD_Grid_monthly_1km_VI|\n',
      'FIELD_NAME = 1 km monthly NDVI\n',
      'BAND_NUMBER = 1\n',
      'SPATIAL_SUBSET_UL_CORNER = ' + str(corner[0]) + '\n',
      'SPATIAL_SUBSET_LR_CORNER = ' + str(corner[1]) + '\n',
      'RESAMPLING_TYPE = BI\n',
      'OUTPUT_PROJECTION_TYPE = UTM\n',
      'ELLIPSOID_CODE = WGS84\n',
      'UTM_ZONE = 50\n'
      'OUTPUT_PROJECTION_PARAMETERS = ( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 )\n',
      'OUTPUT_PIXEL_SIZE = 926.625433056\n',
      'OUTPUT_FILENAME = ' + outpath + '/' + NDVI_date + "_" + eachhdf.split(".")[2] +'_NDVI.tif\n',
      'OUTPUT_TYPE = GEO\n',
      'END\n']
    prmfilename = os.path.join(prmpath, eachhdf+'.prm')
    fo = open(prmfilename,'w',newline='\n')
    fo.writelines(prm)
    fo.close()


for eachhdf in allhdffiles:
    prmfilepath = os.path.join(prmpath, eachhdf + '.prm')
    try:
        resamplefiles = '{0} -P {1}'.format(hegdo, prmfilepath)
        os.system(resamplefiles)        
        print(eachhdf + ' has finished')
    except:
        print(eachhdf + 'was wrong')

# os.system("gdalwarp -srcnodata -3000 -dstnodata -3000 *.tif test.tif")
