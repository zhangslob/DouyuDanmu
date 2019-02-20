#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: kg_qq_test.py 
@time: 2019/02/20
@desc: 
"""
import pytz
import time
import requests
from datetime import datetime


def get_today():
    return datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y_%m_%d %H:%M:%S')


url = 'http://node.kg.qq.com/personal?uid=669d958322283f'
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'http://node.kg.qq.com/play?s=uuzjbYuRZgH-Vuts',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
}

while True:
    try:
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code != 200:
            print('Time: {}, status_code {}, text: {}'.format(get_today(), r.status_code, r.text))

    except:
        pass
