import requests as req
import json

import pandas as pd
import geopandas as gpd
import numpy as np

from scipy.spatial import cKDTree
from pyproj import CRS
from shapely.geometry import Point

def ckdnearest(gdA, gdB, columnName):
    nA = np.array(list(gdA.geometry.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            pd.Series(dist, name=f'{columnName}_dist')
        ], 
        axis=1)

    return gdf

class HouseObject:

    def __init__(self, address):
        self.address = address
        self.buffer_range = ['250', '500', '750']

    def get_current_location(self):
        my_place = self.address
        google_url = f'https://www.google.com.tw/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&q={my_place}'
        res = req.get(google_url)
        google_data = json.loads(res.text[5:])
        self.x = google_data[1][0][1]
        self.y = google_data[1][0][2]
        return self.x, self.y

    def create_buffer(self):
        d = {'idx': [1], 'lon': [self.x], 'lat': [self.y]}
        df = pd.DataFrame(data=d)
        geom = [Point(xy) for xy in zip(df.lon, df.lat)]
        crs = CRS('epsg:4326')
        self.gf = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf = self.gf.to_crs(epsg=3826)  


        self.gf250 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf250 = self.gf250.to_crs(epsg=3826)  
        self.gf250['geometry'] = self.gf250['geometry'].buffer(250)

        self.gf500 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf500 = self.gf500.to_crs(epsg=3826) 
        self.gf500['geometry'] = self.gf500['geometry'].buffer(500)

        self.gf750 = gpd.GeoDataFrame(df, crs=crs, geometry=geom)
        self.gf750 = self.gf750.to_crs(epsg=3826) 
        self.gf750['geometry'] = self.gf750['geometry'].buffer(750)

        self.bufferList = [self.gf250, self.gf500, self.gf750]


    def sjoin_point_layer(self, target_layer, layer_name, layer_join_index_name, join_type):
        i = 0
        for house_buffer in self.bufferList:
            temp_gf = gpd.sjoin(house_buffer, target_layer, how='inner')
            output_point = target_layer[target_layer.index.isin(temp_gf['index_right'])]
            output_point = output_point.to_crs(epsg=4326)
            temp_gf = temp_gf.groupby(temp_gf.index).agg({layer_join_index_name:'count'})
            temp_gf.rename(columns={layer_join_index_name: layer_name + '_' + self.buffer_range[i]}, inplace=True)
            self.gf = self.gf.join(temp_gf)
            if join_type == 'count':
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].isnull(), layer_name+'_'+ self.buffer_range[i]] = 0
            if join_type == 'near':
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].notnull(), layer_name+'_'+ self.buffer_range[i]] = 1
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].isnull(), layer_name+'_'+ self.buffer_range[i]] = 0
            i = i + 1
            if i == 3:
                if join_type == 'near':
                    self.gf = ckdnearest(self.gf, target_layer, layer_name)
                return output_point.to_json()

    def overlay_polygon_layer(self, target_layer, layer_name, layer_join_index_name, join_type):
        i = 0
        for house_buffer in self.bufferList:
            intersection = gpd.overlay(house_buffer, target_layer,  how='intersection', keep_geom_type=True)
            if join_type == 'area':
                intersection["AREA"] = intersection['geometry'].area
                intersection_count = intersection.groupby('idx').agg({"AREA":'sum'})
                intersection_count.rename(columns={'AREA': layer_name+'_'+self.buffer_range[i]}, inplace=True)
            else:
                intersection_count = intersection.groupby('idx').agg({layer_join_index_name:'count'})
                intersection_count.rename(columns={layer_join_index_name: layer_name+'_'+self.buffer_range[i]}, inplace=True)
            self.gf = self.gf.merge(intersection_count,how='left', left_on='idx', right_on='idx')
            if join_type == 'count' or join_type == 'area':
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].isnull(), layer_name+'_'+ self.buffer_range[i]] = 0
            if join_type == 'near':
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].notnull(), layer_name+'_'+ self.buffer_range[i]] = 1
                self.gf.loc[self.gf[layer_name+ '_' + self.buffer_range[i]].isnull(), layer_name+'_'+ self.buffer_range[i]] = 0
            i = i + 1
            if i == 3:
                if join_type == 'near':
                    self.gf = ckdnearest(self.gf, target_layer.centroid, layer_name)
                target_layer['geometry'] = target_layer['geometry'].centroid
                output_point = target_layer[target_layer['full_id'].isin(intersection['full_id'])]
                output_point = output_point.to_crs(epsg=4326)
                return output_point.to_json()

    def return_geo_dataframe(self):
        return self.gf

        #print(type(temp_gf['index_right']))
        #print(temp_gf['geometry'].centroid)