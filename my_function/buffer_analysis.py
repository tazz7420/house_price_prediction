import pandas as pd
import geopandas as gpd
import csv

def buffer_analysis(input_filename, output_filename, preprocessingdata_path):
    gf = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_250 = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_500 = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_750 = gpd.read_file(input_filename, encoding = 'utf-8')
    gf_250['geometry'] = gf_250.buffer(250)
    gf_500['geometry'] = gf_250.buffer(500)
    gf_750['geometry'] = gf_250.buffer(750)
    gf_list = [gf_250, gf_500, gf_750]
    buffer_range = ['250', '500', '750']
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
        
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, clinic_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'CLINIC_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['CLINIC_COUNT_'+ buffer_range[i]].isnull(), 'CLINIC_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
        
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, dentist_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'DENTIST_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['DENTIST_COUNT_'+ buffer_range[i]].isnull(), 'DENTIST_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
        
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, pharmacy_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'機構名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'機構名稱': 'PHARMACY_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['PHARMACY_COUNT_'+ buffer_range[i]].isnull(), 'PHARMACY_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
        
    i = 0
    for house_buffer in gf_list:
        temp_gf = gpd.sjoin(house_buffer, cstore_count, how='inner')
        temp_gf = temp_gf.groupby(temp_gf.index).agg({'分公司名稱':'count'})
        #temp_gf = temp_gf.first()[['機構名稱']]
        temp_gf.rename(columns={'分公司名稱': 'CSTORE_COUNT_' + buffer_range[i]}, inplace=True)
        gf = gf.join(temp_gf)
        gf.loc[gf['CSTORE_COUNT_'+ buffer_range[i]].isnull(), 'CSTORE_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
        
    i = 0
    for house_buffer in gf_list:
        intersection = gpd.overlay(house_buffer, fastfood_count,  how='intersection', keep_geom_type=True)
        intersection_count = intersection.groupby('Unnamed: 0').agg({'full_id':'count'})
        intersection_count.rename(columns={'full_id': 'FASTFOOD_COUNT_'+buffer_range[i]}, inplace=True)
        gf = gf.merge(intersection_count,how='left', left_on='Unnamed: 0', right_on='Unnamed: 0')
        gf.loc[gf['FASTFOOD_COUNT_'+ buffer_range[i]].isnull(), 'FASTFOOD_COUNT_'+ buffer_range[i]] = 0
        i = i + 1
    
    gf.to_csv(output_filename)
    print(gf)