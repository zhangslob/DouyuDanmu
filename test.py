#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: test.py 
@time: 2019/01/10
@desc: 
"""
import time
import pytz
import requests
from datetime import datetime

headers = {
    'origin': 'https://yuba.douyu.com',
    'accept-encoding': 'gzip, deflate, br',
    'x-csrf-token': 'DrsRAga4EcCyk3AboFM8ySQwhBL72mnJ',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'referer': 'https://yuba.douyu.com/p/995429941549108124',
    'authority': 'yuba.douyu.com',
    'cookie': 'dy_did=a17b4ab25c54986f6433ea9b00061501; acf_yb_did=a17b4ab25c54986f6433ea9b00061501; _ga=GA1.2.898345405.1546830910; smidV2=20181222155555157e437e6e4f57b560a3855ffdf9aace007e26097861818f0; wan_auth37wan=d81fa0bf7cf74XaNC0DlLl9qwGKhjiinxQJgs4BM8suz%2F5EJHDn9xlPlxa9vS7xrKgaCHEs72LCyDZ2fYGCOS%2Fb4xf9ye5HjLkqjH3hVs2HipX7YfQ; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1547555261,1548345770,1548650379; Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1548322847,1548651214,1549120614,1550039793; acf_yb_t=DrsRAga4EcCyk3AboFM8ySQwhBL72mnJ; acf_yb_auth=f5a7ccbb0ea2c3629b95014b1ac32e97ab923de3; acf_yb_new_uid=qy70WlRPJAXG; acf_yb_uid=39581553; _gid=GA1.2.822396080.1550039794; _gat_gtag_UA_128072138_1=1; Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1550039801',
}

params = (
    ('timestamp', '0.8287663724619401'),
)

data = {
  'repost': '0',
  'content': '<p>\u72D7\u5B98</p>',
  'pid': '995429941549108124',
  'vo_id': '',
  'tokensign': ''
}


def get_today():
    return datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y_%m_%d %H:%M:%S')


def run():
    try:
        response = requests.post('https://yuba.douyu.com/ybapi/answer/comment', headers=headers, params=params, data=data)
        print('time: {}, status: {}'.format(get_today(), response.json()['status_code']))
    except:
        print('retry')
        time.sleep(30)
        return run()


if __name__ == '__main__':
    while True:
        run()
        time.sleep(10)
