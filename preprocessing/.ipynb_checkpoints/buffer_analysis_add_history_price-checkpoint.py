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

def nearest5HistoryPrice(gdA, gdB):

    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=5)
    gdB_nearest0 = gdB.iloc[idx[:,0]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest0['history_price0'] = gdB_nearest0['單價元平方公尺']
    gdB_nearest0 = gdB_nearest0['history_price0']
    
    gdB_nearest1 = gdB.iloc[idx[:,1]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest1['history_price1'] = gdB_nearest1['單價元平方公尺']
    gdB_nearest1 = gdB_nearest1['history_price1']
    
    gdB_nearest2 = gdB.iloc[idx[:,2]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest2['history_price2'] = gdB_nearest2['單價元平方公尺']
    gdB_nearest2 = gdB_nearest2['history_price2']
    
    gdB_nearest3 = gdB.iloc[idx[:,3]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest3['history_price3'] = gdB_nearest3['單價元平方公尺']
    gdB_nearest3 = gdB_nearest3['history_price3']
    
    gdB_nearest4 = gdB.iloc[idx[:,4]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest4['history_price4'] = gdB_nearest4['單價元平方公尺']
    gdB_nearest4 = gdB_nearest4['history_price4']
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            gdB_nearest0,
            pd.Series(dist[:,0], name=f'有無歷史成交資料'),
            gdB_nearest1,
            pd.Series(dist[:,1], name=f'1_dist'),
            gdB_nearest2,
            pd.Series(dist[:,2], name=f'2_dist'),
            gdB_nearest3,
            pd.Series(dist[:,3], name=f'3_dist'),
            gdB_nearest4,
            pd.Series(dist[:,4], name=f'4_dist')
        ], 
        axis=1)
    gdf.loc[gdf['有無歷史成交資料'] == 0, '有無歷史成交資料'] = 0.0001
    gdf.loc[gdf['1_dist'] == 0, '1_dist'] = 0.0001
    gdf.loc[gdf['2_dist'] == 0, '2_dist'] = 0.0001
    gdf.loc[gdf['3_dist'] == 0, '3_dist'] = 0.0001
    gdf.loc[gdf['4_dist'] == 0, '4_dist'] = 0.0001
    gdf['history_price_same_object'] = gdf.apply(lambda x: (x['history_price0'] * 1 / (x['有無歷史成交資料'] ** 2) + x['history_price1'] * 1 / (x['1_dist'] ** 2) + 
                                                x['history_price2'] * 1 / (x['2_dist'] ** 2) + x['history_price3'] * 1 / (x['3_dist'] ** 2) +
                                                x['history_price4'] * 1 / (x['4_dist'] ** 2))/(1 / (x['有無歷史成交資料'] ** 2) +1 / (x['1_dist'] ** 2) + 
                                                                                               1 / (x['2_dist'] ** 2) +1 / (x['3_dist'] ** 2) +1 / (x['4_dist'] ** 2)), axis = 1)
    gdf.drop(['history_price0', 'history_price1', 'history_price2', 'history_price3', 'history_price4'],axis=1,inplace=True)
    gdf.drop(['1_dist', '2_dist', '3_dist', '4_dist'],axis=1,inplace=True)
    gdf.loc[gdf['有無歷史成交資料'] > 0.0001, '有無歷史成交資料'] = 0
    gdf.loc[gdf['有無歷史成交資料'] == 0.0001, '有無歷史成交資料'] = 1
    return gdf

def nearest5HistoryPrice_age(gdA, gdB):

    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=5)
    gdB_nearest0 = gdB.iloc[idx[:,0]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest0['history_price0'] = gdB_nearest0['單價元平方公尺']
    gdB_nearest0 = gdB_nearest0['history_price0']
    
    gdB_nearest1 = gdB.iloc[idx[:,1]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest1['history_price1'] = gdB_nearest1['單價元平方公尺']
    gdB_nearest1 = gdB_nearest1['history_price1']
    
    gdB_nearest2 = gdB.iloc[idx[:,2]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest2['history_price2'] = gdB_nearest2['單價元平方公尺']
    gdB_nearest2 = gdB_nearest2['history_price2']
    
    gdB_nearest3 = gdB.iloc[idx[:,3]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest3['history_price3'] = gdB_nearest3['單價元平方公尺']
    gdB_nearest3 = gdB_nearest3['history_price3']
    
    gdB_nearest4 = gdB.iloc[idx[:,4]].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest4['history_price4'] = gdB_nearest4['單價元平方公尺']
    gdB_nearest4 = gdB_nearest4['history_price4']
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            gdB_nearest0,
            pd.Series(dist[:,0], name=f'0_dist'),
            gdB_nearest1,
            pd.Series(dist[:,1], name=f'1_dist'),
            gdB_nearest2,
            pd.Series(dist[:,2], name=f'2_dist'),
            gdB_nearest3,
            pd.Series(dist[:,3], name=f'3_dist'),
            gdB_nearest4,
            pd.Series(dist[:,4], name=f'4_dist')
        ], 
        axis=1)
    gdf.loc[gdf['0_dist'] == 0, '0_dist'] = 0.0001
    gdf.loc[gdf['1_dist'] == 0, '1_dist'] = 0.0001
    gdf.loc[gdf['2_dist'] == 0, '2_dist'] = 0.0001
    gdf.loc[gdf['3_dist'] == 0, '3_dist'] = 0.0001
    gdf.loc[gdf['4_dist'] == 0, '4_dist'] = 0.0001
    gdf['history_price_by_house_age'] = gdf.apply(lambda x: (x['history_price0'] * 1 / (x['0_dist'] ** 2) + x['history_price1'] * 1 / (x['1_dist'] ** 2) + 
                                                x['history_price2'] * 1 / (x['2_dist'] ** 2) + x['history_price3'] * 1 / (x['3_dist'] ** 2) +
                                                x['history_price4'] * 1 / (x['4_dist'] ** 2))/(1 / (x['0_dist'] ** 2) +1 / (x['1_dist'] ** 2) + 
                                                                                               1 / (x['2_dist'] ** 2) +1 / (x['3_dist'] ** 2) +1 / (x['4_dist'] ** 2)), axis = 1)
    gdf.drop(['history_price0', 'history_price1', 'history_price2', 'history_price3', 'history_price4'],axis=1,inplace=True)
    gdf.drop(['0_dist','1_dist', '2_dist', '3_dist', '4_dist'],axis=1,inplace=True)
    return gdf

def buffer_analysis(input_filename, output_filename, preprocessingdata_path):
    print("\r",end="")
    print("載入實價登陸圖層:[ =>........................ ]",end="")
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
    print("載入周邊設施圖層:[ ==>....................... ]",end="")
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
    print("環域分析醫院距離:[ ===>...................... ]",end="")
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
    print("環域分析診所數量:[ ====>..................... ]",end="")
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
    print("環域分析牙醫數量:[ =====>.................... ]",end="")
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
    print("環域分析藥局數量:[ ======>................... ]",end="")
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
    print("環域分析超商數量:[ =======>.................. ]",end="")
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
    print("環域分析速食數量:[ ========>................. ]",end="")
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
    print("環域分析圖書館數:[ =========>................ ]",end="")
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
    print("環域分析學校距離:[ ==========>............... ]",end="")
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
    print("環域分析大學距離:[ ===========>.............. ]",end="")
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
    print("環域分析消防距離:[ ============>............. ]",end="")
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
    print("環域分析有無油站:[ =============>............ ]",end="")
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
    print("環域分析有無市場:[ ==============>........... ]",end="")
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
    print("環域分析警局距離:[ ===============>.......... ]",end="")
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
    print("環域分析宮廟數量:[ ================>......... ]",end="")
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
    print("環域分析墳墓面積:[ =================>........ ]",end="")
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
    print("環域分析公園面積:[ ==================>....... ]",end="")
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
    print("環域分析水域面積:[ ===================>...... ]",end="")
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
    print("環域分析停車面積:[ ====================>..... ]",end="")
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
    print("環域分析公車站數:[ =====================>.... ]",end="")
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
    print("環域分析輕軌距離:[ ======================>... ]",end="")
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
    print("環域分析捷運距離:[ =======================>.. ]",end="")
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
    print("環域分析火車距離:[ ========================>. ]",end="")
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
    print("歷史成交價格分析:[ =========================> ]",end="")
    sys.stdout.flush()
    filt_list = ['預售','親','關係','債務','民情','姐妹','母子','兄妹',
                '裝潢','特殊','毛胚','調解','不佳','朋友','夾層','瑕疵',
                '裝修','同一人','急','水','交易','股東',
                '祖孫','破產','轉讓','整修','折讓','毛坯','傢俱','設備']

    for f in filt_list:
        filt = (~gf['備註'].str.contains(f, na=False))
        gf = gf.loc[filt]


    #print(gf.head())
    listA = [110,109,108,107,106,105,104]
    listB = [0,10,20,30,40,50,60]
    listC = ['建物型態-住宅大樓', '建物型態-公寓', '建物型態-華廈', '建物型態-套房', '建物型態-透天']
    listD = ['0', '1']

    j = 0
    for c in listC:
        for d in listD:
            try:
                filt = (gf['交易年份'] != 111) & (gf[c] == 1) & (gf['交易標的'] == d)
                gfb = gf.loc[filt]
                filt = (gf['交易年份'] == 111) & (gf[c] == 1) & (gf['交易標的'] == d)
                gfa = gf.loc[filt]

                gfc = nearest5HistoryPrice(gfa, gfb)
                if j == 0:
                    gf_final = gfc
                    j = j + 1
                else:
                    gf_final = pd.concat([gf_final, gfc])
            except:
                continue

    for a in listA:
        for c in listC:
            for d in listD:
                try:
                    filt = (gf['交易年份'] != 111) & (gf['交易年份'] != a) & (gf[c] == 1) & (gf['交易標的'] == d)
                    gfb = gf.loc[filt]
                    filt = (gf['交易年份'] != 111) & (gf['交易年份'] == a) & (gf[c] == 1) & (gf['交易標的'] == d)
                    gfa = gf.loc[filt]
                    gfc = nearest5HistoryPrice(gfa, gfb)
                    gf_final = pd.concat([gf_final, gfc])
                except:
                    continue

    gf = gf_final

    j = 0
    for b in listB:
        for c in listC:
            for d in listD:
                try:
                    filt = (gf['交易年份'] != 111) & (gf['屋齡'] <= b) & (gf['屋齡'] > b-10) & (gf[c] == 1) & (gf['交易標的'] == d)
                    gfb = gf.loc[filt]
                    filt = (gf['交易年份'] == 111) & (gf['屋齡'] <= b) & (gf['屋齡'] > b-10) & (gf[c] == 1) & (gf['交易標的'] == d)
                    gfa = gf.loc[filt]

                    gfc = nearest5HistoryPrice_age(gfa, gfb)
                    if j == 0:
                        gf_final = gfc
                        j = j + 1
                    else:
                        gf_final = pd.concat([gf_final, gfc])
                except:
                    continue

    for a in listA:
        for b in listB:
            for c in listC:
                for d in listD:
                    try:
                        filt = (gf['交易年份'] != 111) & (gf['交易年份'] != a) & (gf['屋齡'] <= b) & (gf['屋齡'] > b-10) & (gf[c] == 1) & (gf['交易標的'] == d)
                        gfb = gf.loc[filt]
                        filt = (gf['交易年份'] != 111) & (gf['交易年份'] == a) & (gf['屋齡'] <= b) & (gf['屋齡'] > b-10) & (gf[c] == 1) & (gf['交易標的'] == d)
                        gfa = gf.loc[filt]
                        gfc = nearest5HistoryPrice_age(gfa, gfb)
                        gf_final = pd.concat([gf_final, gfc])
                    except:
                        continue
    gf_final.loc[gf_final['有無歷史成交資料'] == 0, 'history_price_same_object'] = 0
    gf_final.loc[gf_final['有無歷史成交資料'] == 1, 'history_price_by_house_age'] = 0
    gf_final['history_price_final'] = gf_final.apply(lambda x: x['history_price_same_object'] + x['history_price_by_house_age'], axis = 1)
    gf_final.drop(['history_price_same_object','history_price_by_house_age'],axis=1,inplace=True)
    gf = gf_final
    
    print("\r",end="")
    print(f"正在儲存檔案至{output_filename}....................................",end="")
    sys.stdout.flush()
    
    
    
    # filt = (gf['交易年份'] != 111) & (gf['屋齡'] < 10) & (gf['建物型態-住宅大樓'] == 1)
    # gfb = gf.loc[filt]
    # filt = (gf['交易年份'] == 110) & (gf['屋齡'] < 10) & (gf['建物型態-住宅大樓'] == 1)
    # gfa = gf.loc[filt]
    # gf = ckdnearest(gfa, gfb)
    #print(gf_final)
    gf.to_csv(output_filename)
    print("\r",end="")
    print(gf.info())
    
if __name__ == '__main__':
    code = input("欲處理的城市簡稱: ")
    buffer_analysis(f'{code}_realprice.geojson', f'../dataset/{code}_model_features_add_history_price.csv', './')