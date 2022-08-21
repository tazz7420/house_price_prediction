import pandas as pd
import geopandas as gpd
import csv, warnings
from shapely.geometry import Point

import sys, os
sys.path.append("..")

def process(cityname):
    warnings.filterwarnings('ignore')
    df_final = pd.read_csv(f'./temp/{cityname}_pre_df_WGS84.csv', encoding = 'utf-8')
    df_final = df_final.dropna(subset=["lon"])
    geom = [Point(xy) for xy in zip(df_final.lon, df_final.lat)]
    crs = {'init': 'epsg:4326'}
    gf_final = gpd.GeoDataFrame(df_final, crs=crs, geometry=geom)
    gf_final = gf_final.to_crs(epsg=3826)    
    gf_final.to_file(f'./geojson/{cityname}_realprice' + ".geojson", driver='GeoJSON')
    print(f'./geojson/{cityname}_realprice.geojson OK!')
    
if __name__ == '__main__':
    code = input("欲處理的{城市簡寫_年份}: ")
    process(code)