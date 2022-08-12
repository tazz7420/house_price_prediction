import geopandas as gpd

def buffer_analysis(filename):
    gf = gpd.read_file(filename, encoding = 'utf-8')
    gf_250 = gpd.read_file(filename, encoding = 'utf-8')
    gf_500 = gpd.read_file(filename, encoding = 'utf-8')
    gf_750 = gpd.read_file(filename, encoding = 'utf-8')
    
