import gdal
import os
import numpy as np


input_dir = "data/BTH_NDVI/2017"
year = "2017"
out_dir = "data/BTH_NDVI_YearNormalized"
src_nodata = -3000

tiff_list = [f for f in os.listdir(input_dir) if f.endswith(".tif")]

ds = gdal.Open(os.path.join(input_dir, tiff_list[0]))
band = ds.GetRasterBand(1)
geo_trans = ds.GetGeoTransform()
proj = ds.GetProjection()
dtaArray = band.ReadAsArray()

resArray = np.zeros((dtaArray.shape[0], dtaArray.shape[1]))
counter = 0
for f in tiff_list:
    ds = gdal.Open(os.path.join(input_dir, f))
    band = ds.GetRasterBand(1)
    dtaArray = band.ReadAsArray()
    resArray = resArray + dtaArray
    counter += 1

resArray = resArray/len(tiff_list)/10000

out_file = os.path.join(out_dir, year+"_NDVI.tiff")
driver = gdal.GetDriverByName("GTiff")
LU_ds = driver.Create(out_file, resArray.shape[1], resArray.shape[0], 1, gdal.GDT_Float32)
LU_ds.GetRasterBand(1).WriteArray(resArray)
LU_ds.GetRasterBand(1).SetNoDataValue(src_nodata/10000)

LU_ds.SetGeoTransform(geo_trans)

LU_ds.SetProjection(proj)
LU_ds.FlushCache()
LU_ds = None
