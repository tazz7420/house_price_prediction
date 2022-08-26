import pandas as pd
import geopandas as gpd
import csv
import re
from shapely.geometry import Point

import sys, os
sys.path.append("..")

def city_filter(geodataframe,cityname):
    gf_city =gpd.read_file(r'../rawdata/city_boundaries/COUNTY_MOI_1090820.shp', encoding = 'utf-8')
    gf_city= gf_city.to_crs(epsg=3826)  
    gf_filter = gf_city[gf_city['COUNTYNAME'] == cityname]
    
    geodataframe = gpd.sjoin(geodataframe, gf_filter)
    
    return geodataframe

def datafilter(cityname, cityname_cn):
    path_text = r'./geojson/'
    path = os.listdir(path_text)
    n = 0
    for filename in path:
        try:
            if (filename.split('_')[0] == cityname):
                if n == 0:
                    gf_final =gpd.read_file(path_text + filename, encoding = 'utf-8')
                    gf_final = gf_final.iloc[1:]
                    gf_final = city_filter(gf_final,cityname_cn)
                    n = n + 1
                    print(f'開啟檔案:{filename}')
                else:
                    gf2 =gpd.read_file(path_text + filename, encoding = 'utf-8')
                    gf2 = gf2.iloc[1:]
                    gf2 = city_filter(gf2,cityname_cn)
                    n = n + 1
                    gf_final = pd.concat([gf_final, gf2])
                    print(f'開啟檔案:{filename}')
        except:
            continue
    
    gf_final.loc[gf_final['交易標的'] == '房地(土地+建物)', '交易標的'] = 0
    gf_final.loc[gf_final['交易標的'] == '房地(土地+建物)+車位', '交易標的'] = 1
    filt = (gf_final['交易標的'] == 1) | (gf_final['交易標的'] == 0)
    gf_final = gf_final.loc[filt]
    gf_final.loc[gf_final['電梯'] == '無', '電梯'] = 0
    gf_final.loc[gf_final['電梯'] == '有', '電梯'] = 1
    gf_final.loc[gf_final['有無管理組織'] == '無', '有無管理組織'] = 0
    gf_final.loc[gf_final['有無管理組織'] == '有', '有無管理組織'] = 1
    # -----車位種類------
    print('車位種類分類中.....')
    data_class = pd.get_dummies(gf_final['車位類別'])
    data_class.columns = ['車位類別_' + str(x) for x in data_class.columns]
    gf_final = pd.concat([gf_final, data_class], axis = 1)
    gf_final.drop(['車位類別'],axis=1,inplace=True)

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
    filt = (gf_final['建物型態'].str.contains('華廈', na=False)) | (gf_final['建物型態'].str.contains('套房', na=False)) | (gf_final['建物型態'].str.contains('公寓', na=False)) | (gf_final['建物型態'].str.contains('住宅大樓', na=False)) | (gf_final['建物型態'].str.contains('透天厝', na=False))
    gf_final = gf_final.loc[filt]
    
    # # -----主要建材-----
    # print('主要建材分類中.....')
    # data_class = pd.get_dummies(gf_final['主要建材'])
    # data_class.columns = ['主要建材_' + str(x) for x in data_class.columns]
    # gf_final = pd.concat([gf_final, data_class], axis = 1)
    # gf_final.drop(['主要建材'],axis=1,inplace=True)
    # gf_final.loc[gf_final['主要建材'].str.contains('鋼筋', na=False), '主要建材_鋼筋'] = 1
    # gf_final.loc[gf_final['主要建材_鋼筋'].isnull() , '主要建材_鋼筋'] = 0
    # gf_final.loc[gf_final['主要建材'].str.contains('鋼骨', na=False), '主要建材_鋼骨'] = 1
    # gf_final.loc[gf_final['主要建材_鋼骨'].isnull() , '主要建材_鋼骨'] = 0
    # gf_final.loc[gf_final['主要建材'].str.contains('混凝土', na=False), '主要建材_混凝土'] = 1
    # gf_final.loc[gf_final['主要建材_混凝土'].isnull() , '主要建材_混凝土'] = 0

    filt = (gf_final['主要建材'].str.contains('鋼筋', na=False)) | (gf_final['主要建材'].str.contains('鋼骨', na=False)) | (gf_final['主要建材'].str.contains('混凝土', na=False))
    gf_final = gf_final.loc[filt]
    
    
    # -----都市使用分區----- '住', '商', '其他', '農', '工'
    # print('都市土地使用分區分類中.....')
    # filt = (gf_final['都市土地使用分區'] == '住') | (gf_final['都市土地使用分區'] == '商') | (gf_final['都市土地使用分區'] == '其他') | (gf_final['都市土地使用分區'] == '農') | (gf_final['都市土地使用分區'] == '工')
    # gf_final = gf_final.loc[filt]
    # data_class = pd.get_dummies(gf_final['都市土地使用分區'])
    # data_class.columns = ['都市土地使用分區_' + str(x) for x in data_class.columns]
    # gf_final = pd.concat([gf_final, data_class], axis = 1)
    # gf_final.drop(['都市土地使用分區'],axis=1,inplace=True)
    
    # -----過濾欄位+資料-----
    print('檔案儲存中.....')
    filt = (gf_final['主要用途'] == '住家用')
    gf_final = gf_final.loc[filt]
    
    gf_final.drop(['index','非都市土地使用分區','非都市土地使用編定','交易年月日','交易筆棟數','移轉層次','建築完成年月',
        '建物移轉總面積平方公尺','總價元','車位移轉總面積(平方公尺)','編號','主建物面積','附屬建物面積','陽台面積',
        '移轉編號','修正地址','index_right','COUNTYID','COUNTYCODE','COUNTYNAME','COUNTYENG',
        '土地移轉總面積平方公尺','總樓層數','建物型態','主要用途'],axis=1,inplace=True)
    gf_final.to_file(f'{cityname}_realprice' + ".geojson", driver='GeoJSON')
    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    cityname_cn = input("欲處理的城市中文名稱: ")
    datafilter(code, cityname_cn)