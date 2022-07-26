import requests as req
import json


def get_current_location(location, header):
    my_place = location
    google_url = f'https://www.google.com.tw/search?tbm=map&authuser=0&hl=zh-TW&gl=tw&q={my_place}'
    res = req.get(google_url, headers = header)
    google_data = json.loads(res.text[5:])
    return google_data[1][0][1], google_data[1][0][2]