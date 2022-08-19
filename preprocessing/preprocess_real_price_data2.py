import pandas as pd
import geopandas as gpd
import csv
import re
from shapely.geometry import Point

import sys, os
sys.path.append("..")
import my_function.buffer_analysis as bas

def process(cityname):
    df_final = pd.read_csv(f'./temp/{cityname}_pre_df_WGS84.csv', encoding = 'utf-8')
    df_final = df_final.dropna(subset=["lon"])
    geom = [Point(xy) for xy in zip(df_final.lon, df_final.lat)]
    crs = {'init': 'epsg:4326'}
    gf_final = gpd.GeoDataFrame(df_final, crs=crs, geometry=geom)
    gf_final = gf_final.to_crs(epsg=3826)
    
    gf_final = gf_final[['Unnamed: 0','鄉鎮市區', '交易年份', '屋齡', '交易標的', '建物型態', '建物現況格局-房', '建物現況格局-廳' ,'建物現況格局-衛', '車位類別', '電梯', 'floor', '單價元平方公尺', 'geometry']]
    gf_final.loc[gf_final['交易標的'] == '房地(土地+建物)', '交易標的'] = 0
    gf_final.loc[gf_final['交易標的'] == '房地(土地+建物)+車位', '交易標的'] = 1
    gf_final.loc[gf_final['電梯'] == '無', '電梯'] = 0
    gf_final.loc[gf_final['電梯'] == '有', '電梯'] = 1
    # -----車位種類------
    print('車位種類分類中.....')
    gf_final.loc[gf_final['車位類別'] == '坡道平面', '車位類別-坡道平面'] = 1
    gf_final.loc[gf_final['車位類別-坡道平面'].isnull() , '車位類別-坡道平面'] = 0
    gf_final.loc[gf_final['車位類別'] == '坡道機械', '車位類別-坡道機械'] = 1
    gf_final.loc[gf_final['車位類別-坡道機械'].isnull() , '車位類別-坡道機械'] = 0
    gf_final.loc[gf_final['車位類別'] == '升降平面', '車位類別-升降平面'] = 1
    gf_final.loc[gf_final['車位類別-升降平面'].isnull() , '車位類別-升降平面'] = 0
    gf_final.loc[gf_final['車位類別'] == '升降機械', '車位類別-升降機械'] = 1
    gf_final.loc[gf_final['車位類別-升降機械'].isnull() , '車位類別-升降機械'] = 0
    gf_final.loc[gf_final['車位類別'] == '一樓平面', '車位類別-一樓平面'] = 1
    gf_final.loc[gf_final['車位類別-一樓平面'].isnull() , '車位類別-一樓平面'] = 0
    gf_final.loc[gf_final['車位類別'] == '塔式車位', '車位類別-塔式車位'] = 1
    gf_final.loc[gf_final['車位類別-塔式車位'].isnull() , '車位類別-塔式車位'] = 0
    gf_final.loc[gf_final['車位類別'] == '其他' , '車位類別-其他'] = 1
    gf_final.loc[gf_final['車位類別-其他'].isnull() , '車位類別-其他'] = 0

    # -----建物型態-----
    print('建物型態分類中.....')
    gf_final.loc[gf_final['建物型態'].str.contains('公寓', na=False), '建物型態-公寓'] = 1
    gf_final.loc[gf_final['建物型態-公寓'].isnull() , '建物型態-公寓'] = 0
    gf_final.loc[gf_final['建物型態'].str.contains('華廈', na=False), '建物型態-華廈'] = 1
    gf_final.loc[gf_final['建物型態-華廈'].isnull() , '建物型態-華廈'] = 0
    gf_final.loc[gf_final['建物型態'].str.contains('住宅大樓', na=False), '建物型態-住宅大樓'] = 1
    gf_final.loc[gf_final['建物型態-住宅大樓'].isnull() , '建物型態-住宅大樓'] = 0
    gf_final.loc[gf_final['建物型態'].str.contains('套房', na=False), '建物型態-套房'] = 1
    gf_final.loc[gf_final['建物型態-套房'].isnull() , '建物型態-套房'] = 0
    gf_final.loc[gf_final['建物型態'].str.contains('透天', na=False), '建物型態-透天'] = 1
    gf_final.loc[gf_final['建物型態-透天'].isnull() , '建物型態-透天'] = 0
    
    gf_final.to_file(f'{cityname}_realprice' + ".geojson", driver='GeoJSON')
    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    process(code)