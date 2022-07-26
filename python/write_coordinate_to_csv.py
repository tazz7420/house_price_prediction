import csv
import cn2an
import sys
import re
from time import sleep
from random import randint
import pandas as pd

import python.google_map_spider as gms
from fake_useragent import UserAgent
ua = UserAgent(cache=True) # cache=True 表示從已經儲存的列表中提取

def write(inputFile, outputFile, column, fix_address):
    # 載入pabdas讀取資料數量用作進度條用
    df = pd.read_csv(inputFile)
    data_count = len(df)
    
    # fake user agent 反反爬蟲用
    headers = {
        'user-agent': ua.random
    }
    
    # 正規表達式(中文數字轉阿拉伯數字)
    pattern = r'[0-9]*?[零一二三四五六七八九十]*?[0-9]*?[零一二三四五六七八九十]{1}[0-9]*?[號]'
    # 開啟 CSV 檔案
    with open(inputFile, newline='') as csvfile:

        # 讀取 CSV 檔案內容
        rows = csv.reader(csvfile)

    
        timeup = 0
        line = 1
        # 以迴圈輸出每一列
        for row in rows:
            result = []
            
            # 欄位名稱
            if line == 1:
                row.append('lon')
                row.append('lat')
                result.append(row)
                line = line+1
                with open(outputFile, 'w', newline='') as csvfile1:
                    writer = csv.writer(csvfile1,delimiter=',')
                    writer.writerows(result)
                continue
            
            # 反反爬蟲用
            if timeup % 20 == 0:
                if timeup % 100 == 0:
                    headers = {
                        'user-agent': ua.random
                    }
                sleep(randint(2,4))
            
            # 地址轉坐標
            try:
                # 地址中 中文xx號轉成阿拉伯數字xx號
                if row[fix_address] == "True":
                    m = re.search(pattern, f"{row[column].split('號')[0]}號")
                    m.group(0)
                    n = f"{row[column].split('號')[0]}號"
                    nn = n.split(m.group(0))[0]
                    to_an = cn2an.cn2an(m.group(0).split('號')[0], "smart")
                    #if to_an == ' ':
                        #to_an = cn2an.cn2an(m.group(0).split('號')[0], "normal")
                    address = str(nn) + str(to_an) + '號'
                else:
                    address = f"{row[column].split('號')[0]}號"
                # 取得坐標
                lon, lat = gms.get_current_location(address, headers)
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
            with open(outputFile, 'a+', newline='') as csvfile1:
                writer = csv.writer(csvfile1,delimiter=',')
                writer.writerows(result)