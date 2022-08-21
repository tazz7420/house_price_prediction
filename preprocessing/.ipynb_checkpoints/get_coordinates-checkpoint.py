import pandas as pd
import geopandas as gpd
import csv
import re
from shapely.geometry import Point

import sys, os
sys.path.append("..")
import my_function.full_to_half as htf
import my_function.write_coordinate_to_csv as wctc

def process(year, input_citycode, output_cityname):
    path_text = r'../rawdata/real_price/'
    path = os.listdir(path_text)
    n = 0
    for filename in path:
        try:
            if (filename[-3:] == 'csv') & (filename.split('_')[2] == input_citycode)& (filename.split('_')[0] == year):
                if n == 0:
                    df1 = pd.read_csv(path_text + filename, encoding = 'utf-8')
                    df1 = df1.iloc[1:]
                    n = n + 1
                    print(f'開啟檔案:{filename}')
                else:
                    df2 = pd.read_csv(path_text + filename, encoding = 'utf-8')
                    df2 = df2.iloc[1:]
                    df1 = pd.concat([df1, df2])
                    print(f'開啟檔案:{filename}')
        except:
            continue
    
    filt = (df1['電梯'].isnull()) & (df1['建物型態'].str.contains('有電梯', na=False))
    df1.loc[filt,['電梯']] = '有'
    filt = (df1['電梯'].isnull())
    df1.loc[filt,['電梯']] = '無'
    filt = (df1['主要用途'] == '住家用') & (~df1['備註'].str.contains('親友', na=False)) & (~df1['備註'].str.contains('預售屋', na=False)) & (~df1['備註'].str.contains('地上權', na=False)) & (~df1['備註'].str.contains('夾層', na=False)) & ((df1['交易標的'] == '房地(土地+建物)') | (df1['交易標的'] == '房地(土地+建物)+車位'))
    pre_df = df1.loc[filt,['土地位置建物門牌','鄉鎮市區','交易標的','交易年月日','建築完成年月','建物型態','主要建材','建物現況格局-房','建物現況格局-廳','建物現況格局-衛','車位類別','電梯','單價元平方公尺']]
    pre_df = pre_df.dropna(subset=["單價元平方公尺"])
    pre_df = pre_df.dropna(subset=["建築完成年月"])
    pre_df['屋齡']=pre_df['交易年月日'].str[0:3].astype(float)-pre_df['建築完成年月'].str[0:3].astype(float)
    pre_df['交易年份']=pre_df['交易年月日'].str[0:3]
    pre_df.reset_index(inplace=True, drop=False)
    filt2 = (pre_df['屋齡'] >= 0)
    pre_df = pre_df.loc[filt2,['交易年份','土地位置建物門牌','鄉鎮市區','屋齡','交易標的','交易年月日','建築完成年月','建物型態','主要建材','建物現況格局-房','建物現況格局-廳','建物現況格局-衛','車位類別','電梯','單價元平方公尺']]
    
    pattern = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]{1}[0-9]*?[號]'
    pre_df['修正地址'] = pre_df['土地位置建物門牌'].str.contains(pattern,regex=True)
    pre_df['土地位置建物門牌'] = htf.h2f(pre_df['土地位置建物門牌'])
    pre_df.to_csv(f'./temp/{output_cityname}_pre_df.csv')
    wctc.write(f'./temp/{output_cityname}_pre_df.csv', f'./temp/{output_cityname}_pre_df_WGS84.csv', 2,14)
    
if __name__ == '__main__':
    year = input("欲處理的年份: ")
    code = input("欲處理的城市代號: ")
    name = input("欲輸出的檔案名稱: ")
    process(year,code,name)