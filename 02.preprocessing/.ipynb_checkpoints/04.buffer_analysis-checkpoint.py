import pandas as pd
import geopandas as gpd
import csv, sys
import numpy as np

from scipy.spatial import cKDTree
from shapely.geometry import Point

def ckdnearest(gdA, gdB, columnName):

    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    #gdB_nearest = gdB.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            pd.Series(dist, name=f'{columnName}_dist')
        ], 
        axis=1)

    return gdf


def buffer_analysis(input_filename, output_filename, preprocessingdata_path):
    print("\r",end="")
    print("載入實價登錄圖層...... ||  [ >........................ ]",end="")
    sys.stdout.flush()
    
    gf = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_250 = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_500 = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_750 = gpd.read_file(input_filename, encoding = 'utf-8')

    gf_250['geometry'] = gf_250.buffer(250)
    gf_500['geometry'] = gf_500.buffer(500)
    gf_750['geometry'] = gf_750.buffer(750)
    gf_list = [gf_250, gf_500, gf_750]
    buffer_range = ['250', '500', '750']
    
    print("\r",end="")
    print("載入周邊設施圖層...... ||  [ =>....................... ]",end="")
    sys.stdout.flush()
    
    # 醫療設施medical_facilities
    near_hospital = gpd.read_file(preprocessingdata_path + 'medical_facilities/hospital.geojson', encoding = 'utf-8') # point
    clinic_count = gpd.read_file(preprocessingdata_path + 'medical_facilities/clinic.geojson', encoding = 'utf-8') # point
    dentist_count = gpd.read_file(preprocessingdata_path + 'medical_facilities/dentist.geojson', encoding = 'utf-8') # point
    pharmacy_count = gpd.read_file(preprocessingdata_path + 'medical_facilities/pharmacy.geojson', encoding = 'utf-8') # point
    # 經濟指標economic_indicators
    cstore_count = gpd.read_file(preprocessingdata_path + 'economic_indicators/conveniencestore.geojson', encoding = 'utf-8') # point
    fastfood_count = gpd.read_file(preprocessingdata_path + 'economic_indicators/fastfood.geojson', encoding = 'utf-8') # polygon
    # 教育資源educational_resources
    library_count = gpd.read_file(preprocessingdata_path + 'educational_resources/library.geojson', encoding = 'utf-8') # polygon
    near_school = gpd.read_file(preprocessingdata_path + 'educational_resources/school.geojson', encoding = 'utf-8') # polygon
    near_university = gpd.read_file(preprocessingdata_path + 'educational_resources/university.geojson', encoding = 'utf-8') # polygon
    # 公共安全public_safety
    near_firestation = gpd.read_file(preprocessingdata_path + 'public_safety/firestation.geojson', encoding = 'utf-8') # point
    near_fuel = gpd.read_file(preprocessingdata_path + 'public_safety/fuel.geojson', encoding = 'utf-8') # polygon
    near_market = gpd.read_file(preprocessingdata_path + 'public_safety/market.geojson', encoding = 'utf-8') # polygon
    near_police = gpd.read_file(preprocessingdata_path + 'public_safety/police.geojson', encoding = 'utf-8') # point
    temple_count = gpd.read_file(preprocessingdata_path + 'public_safety/placeofworkship.geojson', encoding = 'utf-8') # polygon
    # 自然環境natural_environment
    cemetery_area = gpd.read_file(preprocessingdata_path + 'natural_environment/cemetery.geojson', encoding = 'utf-8') # polygon
    park_area = gpd.read_file(preprocessingdata_path + 'natural_environment/park.geojson', encoding = 'utf-8') # polygon
    river_area = gpd.read_file(preprocessingdata_path + 'natural_environment/river_TW.geojson', encoding = 'utf-8') # polygon
    # 交通運輸transportation
    stop_count = gpd.read_file(preprocessingdata_path + 'transportation/busstop.geojson', encoding = 'utf-8') # point
    near_lrt = gpd.read_file(preprocessingdata_path + 'transportation/LRT.geojson', encoding = 'utf-8') # point
    near_mrt = gpd.read_file(preprocessingdata_path + 'transportation/MRT.geojson', encoding = 'utf-8') # point
    near_tra = gpd.read_file(preprocessingdata_path + 'transportation/TRA.geojson', encoding = 'utf-8') # point
    parking_area = gpd.read_file(preprocessingdata_path + 'transportation/parking.geojson', encoding = 'utf-8') # polygon
    
    print("\r",end="")
    print("環域分析醫院距離...... ||  [ ==>...................... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_hospital, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'NEAR_HOSTIPAL_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_HOSTIPAL_' + buffer_range[i]].notnull(), 'NEAR_HOSTIPAL_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_HOSTIPAL_'+ buffer_range[i]].isnull(), 'NEAR_HOSTIPAL_'+ buffer_range[i]] = 0
        i = i + 1
    
    gf = ckdnearest(gf,near_hospital,'near_hospital')
    
    print("\r",end="")
    print("環域分析診所數量...... ||  [ ===>..................... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, clinic_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'CLINIC_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['CLINIC_COUNT_'+ buffer_range[i]].isnull(), 'CLINIC_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析牙醫數量...... ||  [ ====>.................... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, dentist_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'DENTIST_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['DENTIST_COUNT_'+ buffer_range[i]].isnull(), 'DENTIST_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析藥局數量...... ||  [ =====>................... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, pharmacy_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'PHARMACY_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['PHARMACY_COUNT_'+ buffer_range[i]].isnull(), 'PHARMACY_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析超商數量...... ||  [ ======>.................. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, cstore_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'分公司名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'分公司名稱': 'CSTORE_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['CSTORE_COUNT_'+ buffer_range[i]].isnull(), 'CSTORE_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析速食數量...... ||  [ =======>................. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, fastfood_count,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'FASTFOOD_COUNT_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['FASTFOOD_COUNT_'+ buffer_range[i]].isnull(), 'FASTFOOD_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析圖書館數...... ||  [ ========>................ ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, library_count,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'LIBRARY_COUNT_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['LIBRARY_COUNT_'+ buffer_range[i]].isnull(), 'LIBRARY_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析學校距離...... ||  [ =========>............... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, near_school,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'NEAR_SCHOOL_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['NEAR_SCHOOL_'+ buffer_range[i]].notnull(), 'NEAR_SCHOOL_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_SCHOOL_'+ buffer_range[i]].isnull(), 'NEAR_SCHOOL_'+ buffer_range[i]] = 0
        i = i + 1
        
    gf = ckdnearest(gf,near_school.centroid, 'near_school')
    
    print("\r",end="")
    print("環域分析大學距離...... ||  [ ==========>.............. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, near_university,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'NEAR_UNIVERSITY_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['NEAR_UNIVERSITY_'+ buffer_range[i]].notnull(), 'NEAR_UNIVERSITY_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_UNIVERSITY_'+ buffer_range[i]].isnull(), 'NEAR_UNIVERSITY_'+ buffer_range[i]] = 0
        i = i + 1
        
    gf = ckdnearest(gf,near_university.centroid, 'near_university_dist')
    
    print("\r",end="")
    print("環域分析消防距離...... ||  [ ===========>............. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_firestation, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['消防隊名稱']]
        temp_gf.rename(columns={'消防隊名稱': 'NEAR_FIRESTATION_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_FIRESTATION_' + buffer_range[i]].notnull(), 'NEAR_FIRESTATION_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_FIRESTATION_'+ buffer_range[i]].isnull(), 'NEAR_FIRESTATION_'+ buffer_range[i]] = 0
        i = i + 1
    
    gf = ckdnearest(gf,near_firestation,'near_firestation')
    
    print("\r",end="")
    print("環域分析近加油站...... ||  [ ============>............ ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, near_fuel,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'NEAR_FUEL_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['NEAR_FUEL_'+ buffer_range[i]].notnull(), 'NEAR_FUEL_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_FUEL_'+ buffer_range[i]].isnull(), 'NEAR_FUEL_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析近菜市場...... ||  [ =============>........... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, near_market,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'NEAR_MARKET_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['NEAR_MARKET_'+ buffer_range[i]].notnull(), 'NEAR_MARKET_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_MARKET_'+ buffer_range[i]].isnull(), 'NEAR_MARKET_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析警局距離...... ||  [ ==============>.......... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_police, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['中文單位名稱']]
        temp_gf.rename(columns={'中文單位名稱': 'NEAR_POLICE_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_POLICE_' + buffer_range[i]].notnull(), 'NEAR_POLICE_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_POLICE_'+ buffer_range[i]].isnull(), 'NEAR_POLICE_'+ buffer_range[i]] = 0
        i = i + 1
    
    gf = ckdnearest(gf,near_police,'near_police')
    
    print("\r",end="")
    print("環域分析宮廟數量...... ||  [ ===============>......... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, temple_count,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'TEMPLE_COUNT_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['TEMPLE_COUNT_'+ buffer_range[i]].isnull(), 'TEMPLE_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析墓地面積...... ||  [ ================>........ ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, cemetery_area,  how='intersection', keep_geom_type=True)
        intersection['CEMETERY_AREA'] = intersection['geometry'].area
        intersection_count = intersection.groupby('Unnamed: 0').agg({'CEMETERY_AREA':'sum'})
        intersection_count.rename(columns={'CEMETERY_AREA': 'CEMETERY_AREA_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['CEMETERY_AREA_'+ buffer_range[i]].isnull(), 'CEMETERY_AREA_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析公園面積...... ||  [ =================>....... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, park_area,  how='intersection', keep_geom_type=True)
        intersection['PARK_AREA'] = intersection['geometry'].area
        intersection_count = intersection.groupby('Unnamed: 0').agg({'PARK_AREA':'sum'})
        intersection_count.rename(columns={'PARK_AREA': 'PARK_AREA_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['PARK_AREA_'+ buffer_range[i]].isnull(), 'PARK_AREA_'+ buffer_range[i]] = 0
        i = i + 1
    

    print("\r",end="")
    print("環域分析水域面積...... ||  [ ==================>...... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, river_area,  how='intersection', keep_geom_type=True)
        intersection['WATER_AREA'] = intersection['geometry'].area
        intersection_count = intersection.groupby('Unnamed: 0').agg({'WATER_AREA':'sum'})
        intersection_count.rename(columns={'WATER_AREA': 'WATER_AREA_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['WATER_AREA_'+ buffer_range[i]].isnull(), 'WATER_AREA_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析停車面積...... ||  [ ===================>..... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, parking_area,  how='intersection', keep_geom_type=True)
        intersection['PARKING_AREA'] = intersection['geometry'].area
        intersection_count = intersection.groupby('Unnamed: 0').agg({'PARKING_AREA':'sum'})
        intersection_count.rename(columns={'PARKING_AREA': 'PARKING_AREA_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['PARKING_AREA_'+ buffer_range[i]].isnull(), 'PARKING_AREA_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析公車站數...... ||  [ ====================>.... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, stop_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'full_id':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'full_id': 'STOP_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['STOP_COUNT_'+ buffer_range[i]].isnull(), 'STOP_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    print("\r",end="")
    print("環域分析輕軌距離...... ||  [ =====================>... ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_lrt, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['MARKID']]
        temp_gf.rename(columns={'MARKID': 'NEAR_LRT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_LRT_' + buffer_range[i]].notnull(), 'NEAR_LRT_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_LRT_'+ buffer_range[i]].isnull(), 'NEAR_LRT_'+ buffer_range[i]] = 0
        i = i + 1
        
    gf = ckdnearest(gf,near_lrt,'near_lrt')
    
    print("\r",end="")
    print("環域分析捷運距離...... ||  [ ======================>.. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_mrt, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['MARKID']]
        temp_gf.rename(columns={'MARKID': 'NEAR_MRT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_MRT_' + buffer_range[i]].notnull(), 'NEAR_MRT_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_MRT_'+ buffer_range[i]].isnull(), 'NEAR_MRT_'+ buffer_range[i]] = 0
        i = i + 1
    
    gf = ckdnearest(gf,near_mrt,'near_mrt')
    
    print("\r",end="")
    print("環域分析火車距離...... ||  [ =======================>. ]",end="")
    sys.stdout.flush()
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, near_tra, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index)
        temp_gf = temp_gf.first()[['MARKID']]
        temp_gf.rename(columns={'MARKID': 'NEAR_TRA_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['NEAR_TRA_' + buffer_range[i]].notnull(), 'NEAR_TRA_'+ buffer_range[i]] = 1
        gf.loc[gf['NEAR_TRA_'+ buffer_range[i]].isnull(), 'NEAR_TRA_'+ buffer_range[i]] = 0
        i = i + 1
        
    gf = ckdnearest(gf,near_tra,'near_tra')
    
    
    print("\r",end="")
    print("完成分析儲存檔案...... ||  [ ========================> ]",end="")
    sys.stdout.flush()
    gf.to_csv(output_filename)

    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    buffer_analysis(f'../03.dataset/{code}_realprice.geojson', f'../03.dataset/{code}_model_features.csv', './')