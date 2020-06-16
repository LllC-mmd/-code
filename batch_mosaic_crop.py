import os

NoData = -3000
bd_path = "BTH_region.shp"
tiffDir = "tiff_data"
saveDir = "tiff_data/mosaic"
tiff_list = [f for f in os.listdir(tiffDir) if f.endswith(".tif")]

# group by date
tiff_group = {}
for tiff in tiff_list:
    NDVI_date = tiff.split("_")[0]
    if NDVI_date in tiff_group.keys():
        tiff_group[NDVI_date].append(tiff)
    else:
        tiff_group[NDVI_date] = [tiff]

# mosaic
for k, v in tiff_group.items():
    os.system("gdalwarp -srcnodata {0} -dstnodata {1} {2} {3}".format(NoData, NoData, " ".join([os.path.join(tiffDir,i) for i in v]),
                                                                      os.path.join(saveDir, "temp_"+k+"_.tif")))

# crop using boundary
temp_list = [f for f in os.listdir(saveDir) if f.endswith(".tif")]
for temp in temp_list:
    NDVI_date = temp.split("_")[1]
    os.system("gdalwarp -of GTiff -cutline {0} -crop_to_cutline {1} {2}".format(bd_path, os.path.join(saveDir, temp), 
                                                                                            os.path.join(saveDir, NDVI_date+".tif")))

os.system("rm -rf tiff_data/mosaic/temp*")
