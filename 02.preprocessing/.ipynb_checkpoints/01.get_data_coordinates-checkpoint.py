import pandas as pd
import geopandas as gpd
import requests as req
import csv, cn2an, re, sys, os, json
from time import sleep
from random import randint
from shapely.geometry import Point
from fake_useragent import UserAgent
sys.path.append("..")

# 透過GOOGLE MAP的網址列轉址
def get_current_location(location, header):
    my_place = location
    google_url = f'https://www.google.com.tw/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&q={my_place}'
    res = req.get(google_url, headers = header)
    google_data = json.loads(res.text[5:])
    return google_data[1][0][1], google_data[1][0][2]

# 全形數字轉半形數字
def f2h(dataseries):
    full_cha = ['０', '１','２','３','４','５','６','７','８','９']
    num = 0
    for c in full_cha:
        dataseries = dataseries.str.replace(str(c),str(num))
        num = num + 1
    return dataseries

# 取得座標之前需對地址做前處理
def get_coordinate(inputFile, outputFile, address_column, total_floor_column, fix_address):
    ua = UserAgent(cache=True) # cache=True 表示從已經儲存的列表中提取
    # 載入pabdas讀取資料數量用作進度條用
    df = pd.read_csv(inputFile)
    data_count = len(df)
    
    # fake user agent 反反爬蟲用
    headers = {
        'user-agent': ua.random
    }
    
    # 正規表達式(中文數字轉阿拉伯數字)
    pattern = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]{1}[0-9]*?[號]'
    pattern2 = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[樓]'
    pattern3 = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[層]'
    # 開啟 CSV 檔案
    with open(inputFile, newline='', encoding='utf-8') as csvfile:

        # 讀取 CSV 檔案內容
        rows = csv.reader(csvfile)
        
        timeup = 0
        line = 1
        # 以迴圈輸出每一列
        for row in rows:
            result = []
            
            # 欄位名稱
            if line == 1:
                row.append('floor')
                row.append('total_floor')
                row.append('lon')
                row.append('lat')
                result.append(row)
                line = line+1
                with open(outputFile, 'w', newline='', encoding='utf-8') as csvfile1:
                    writer = csv.writer(csvfile1,delimiter=',')
                    writer.writerows(result)
                continue
            
            # 反反爬蟲用
            if timeup % 30 == 0:
                if timeup % 150 == 0:
                    headers = {
                        'user-agent': ua.random
                    }
                sleep(randint(2,4))
            
            # 樓層中文數字轉阿拉伯數字
            #print(row[column])
            try:
                m2 = re.search(pattern3, f"{row[total_floor_column-1].split('層')[0]}層")
                m2.group(0)
                n2 = f"{row[total_floor_column-1].split('層')[0]}層"
                nn2 = n2.split(m2.group(0))[0]
                to_an2 = cn2an.cn2an(m2.group(0).split('層')[0], "smart")
                floor = to_an2
            
            # 無法取得坐標 值=null
            except:
                # 樓層中文數字轉阿拉伯數字
                #print(row[column])
                try:
                    m2 = re.search(pattern2, f"{row[address_column].split('樓')[0]}樓")
                    m2.group(0)
                    n2 = f"{row[address_column].split('樓')[0]}樓"
                    nn2 = n2.split(m2.group(0))[0]
                    to_an2 = cn2an.cn2an(m2.group(0).split('樓')[0], "smart")
                    floor = to_an2

                # 無法取得坐標 值=null
                except:
                    m2 = re.search(pattern2, f"{row[address_column].split('樓')[0]}樓")
                    m2.group(0)
                    floor = m2.group(0)

            if floor == '樓':
                floor = 1
            try:
                row.append(int(floor))
            except:
                row.append('null')
            
            
                
            # 總樓層中文數字轉阿拉伯數字
            #print(row[column])
            try:
                m2 = re.search(pattern3, f"{row[total_floor_column].split('層')[0]}層")
                m2.group(0)
                n2 = f"{row[total_floor_column].split('層')[0]}層"
                nn2 = n2.split(m2.group(0))[0]
                to_an2 = cn2an.cn2an(m2.group(0).split('層')[0], "smart")
                floor = to_an2
            
            # 無法取得坐標 值=null
            except:
                m2 = re.search(pattern3, f"{row[total_floor_column].split('層')[0]}層")
                m2.group(0)
                floor = m2.group(0)
            
            if floor == '層':
                floor = 1
            try:
                row.append(int(floor))
            except:
                row.append('null')
            
            # 地址轉坐標
            try:
                # 地址中 中文xx號轉成阿拉伯數字xx號
                if row[fix_address] == "True":
                    m = re.search(pattern, f"{row[address_column].split('號')[0]}號")
                    m.group(0)
                    n = f"{row[address_column].split('號')[0]}號"
                    nn = n.split(m.group(0))[0]
                    to_an = cn2an.cn2an(m.group(0).split('號')[0], "smart")
                    #if to_an == ' ':
                        #to_an = cn2an.cn2an(m.group(0).split('號')[0], "normal")
                    address = str(nn) + str(to_an) + '號'
                else:
                    address = f"{row[address_column].split('號')[0]}號"
                # 取得坐標
                lon, lat = get_current_location(address, headers)
                row.append(lon)
                row.append(lat)
                #print(f"取得  {address}  坐標")
            
            # 無法取得坐標 值=null
            except:
                headers = {
                    'user-agent': ua.random
                }
                row.append('null')
                row.append('null')
                #print(f"{line}:{row[column].split('號')[0]}號，需手動查詢以及更換headers")
                sleep(10)
            timeup = timeup + 1
            #sleep(randint(1,2))
            result.append(row)
            
            # 進度條顯示
            percentage = round((line-1)*100/(data_count),4)
            print("\r",end="")
            print("progress: {:.4f}%: ".format(percentage),"▋" * (int(percentage)//2),end="")
            sys.stdout.flush()

            line = line+1
            # 資料寫入新的CSV
            with open(outputFile, 'a+', newline='', encoding='utf-8') as csvfile1:
                writer = csv.writer(csvfile1,delimiter=',')
                writer.writerows(result)


def process(year, input_citycode, output_cityname):
    path_text = r'../01.rawdata/real_price/'
    path = os.listdir(path_text)
    n = 0
    # 結合不同年份資料
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
    
    # 處理電梯欄位為空值的資料
    filt = (df1['電梯'].isnull()) & (df1['建物型態'].str.contains('有電梯', na=False))
    df1.loc[filt,['電梯']] = '有'
    filt = (df1['電梯'].isnull())
    df1.loc[filt,['電梯']] = '無'
    
    # 清理沒有建築完成年月的空值
    df1 = df1.dropna(subset=["建築完成年月"])
    
    # 計算屋齡
    df1['屋齡']=df1['交易年月日'].str[0:3].astype(float)-df1['建築完成年月'].str[0:3].astype(float)
    df1['交易年份']=df1['交易年月日'].str[0:3]
    df1.reset_index(inplace=True, drop=False)
    df1 = df1[df1['屋齡'] >= 0]

    # 尋找需修正地址的資料
    pattern = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]{1}[0-9]*?[號]'
    df1['修正地址'] = df1['土地位置建物門牌'].str.contains(pattern,regex=True)
    df1['土地位置建物門牌'] = f2h(df1['土地位置建物門牌'])
    df1.to_csv(f'./--temp--/{output_cityname}_pre_df.csv')
    get_coordinate(f'./--temp--/{output_cityname}_pre_df.csv', f'./--temp--/{output_cityname}_pre_df_WGS84.csv', 4, 12,37)
    
if __name__ == '__main__':
    year = input("欲處理的年份: ")
    code = input("欲處理的城市代號: ")
    name = input("欲輸出的檔案名稱: ")
    process(year,code,name)