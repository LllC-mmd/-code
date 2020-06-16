import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import os

import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely import geometry


def getCityMean(bd_path, raster_file, addrCode_ref):
    bd_shp = gpd.read_file(bd_path, encoding="GBK")
    num_city = len(bd_shp["adcode"])

    # access to boundary Shapely Polygon using cities' boundary info
    bd_dict = {}
    for i in range(0, num_city):
        z = bd_shp.iloc[i, :]
        if z.geometry.type == "Polygon":
            bd_dict[z["adcode"]] = [geometry.Polygon(z.geometry)]
        else:
            bd_dict[z["adcode"]] = [geometry.MultiPolygon(z.geometry)]

    city_mean_dict = {}
    for i in range(0, num_city):
        addr_code = bd_shp.iloc[i]["adcode"]
        with rasterio.open(raster_file) as src:
            raster_image, geo_transform = mask(src, bd_dict[addr_code], nodata=src.nodata, pad_width=0.5, crop=True)
            city_mean = np.mean(np.ma.masked_where(raster_image == src.nodata, raster_image))
            city_mean_dict[addrCode_ref[addr_code]] = city_mean
    return city_mean_dict


addrCode_ref = {110101: "东城区", 110102: "西城区", 110105: "朝阳区", 110106: "丰台区", 110107: "石景山区",
                110108: "海淀区", 110109: "门头沟区", 110111: "房山区", 110112: "通州区", 110113: "顺义区",
                110114: "昌平区", 110115: "大兴区", 110116: "怀柔区", 110117: "平谷区", 110118: "密云区",
                110119: "延庆区",
                120101: "和平区", 120102: "河东区", 120103: "河西区", 120104: "南开区", 120105: "河北区",
                120106: "红桥区", 120110: "东丽区", 120111: "西青区", 120112: "津南区", 120113: "北辰区",
                120114: "武清区", 120115: "宝坻区", 120116: "滨海新区", 120117: "宁河区", 120118: "静海区",
                120119: "蓟州区",
                130100: "石家庄市", 130200: "唐山市", 130300: "秦皇岛市", 130400: "邯郸市", 130500: "邢台市",
                130600: "保定市", 130700: "张家口市", 130800: "承德市", 130900: "沧州市", 131000: "廊坊市",
                131100: "衡水市"}


excel_path = "data/BTHData.xlsx"
ntl_data = pd.read_excel(excel_path, sheet_name="NNTI", index_col=u'城市名称')
ndvi_data = pd.read_excel(excel_path, sheet_name="NDVI", index_col=u'城市名称')
ah_data = pd.read_excel(excel_path, sheet_name="AH", index_col=u'城市名称')

cityList = ntl_data.index.tolist()

features = []
y_ah = []
for city in cityList:
    ntl_i = np.array(ntl_data.loc[city])
    ndvi_i = np.array(ndvi_data.loc[city])
    hsi_i = (1.0 - ndvi_i + ntl_i) / (1.0 - ntl_i + ndvi_i + ntl_i * ndvi_i)
    features = features + hsi_i.tolist()
    y_ah = y_ah + ah_data.loc[city].tolist()

# reshape to (n_samples, n_features)
features = np.array(features).reshape(-1, 1)
y_ah = np.array(y_ah).reshape(-1, 1)

poly = PolynomialFeatures(degree=2)
poly_features = poly.fit_transform(features)
lr_model = LinearRegression(fit_intercept=False)
lr_model.fit(poly_features, y_ah)

print(lr_model.coef_)
print(lr_model.score(poly_features, y_ah))

'''
# output NTI data
bd_path = "data/BTH_region.shp"
raster_dir = "data/BTH_NTI_YearNormalized"
year = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]

city_NTI = {}
for k,v in addrCode_ref.items():
    city_NTI[v] = []

raster_file = [f for f in os.listdir(raster_dir) if f.endswith(".tiff")]
for y in year:
    city_avg = getCityMean(bd_path, os.path.join(raster_dir, y+"_NTI.tiff"), addrCode_ref)
    for k,v in city_avg.items():
        city_NTI[k].append(v)

for k,v in city_NTI.items():
    print(k, "\t", "\t".join(map(lambda x: "{:.5f}".format(x), v)))
'''

'''
# output NDVI data
bd_path = "data/BTH_region.shp"
raster_dir = "data/BTH_NDVI_YearNormalized"
year = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017"]

city_NDVI = {}
for k,v in addrCode_ref.items():
    city_NDVI[v] = []

raster_file = [f for f in os.listdir(raster_dir) if f.endswith(".tiff")]
for y in year:
    city_avg = getCityMean(bd_path, os.path.join(raster_dir, y+"_NDVI.tiff"), addrCode_ref)
    for k,v in city_avg.items():
        city_NDVI[k].append(v)

for k,v in city_NDVI.items():
    print(k, "\t", "\t".join(map(lambda x: "{:.5f}".format(x), v)))
'''