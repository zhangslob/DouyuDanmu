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
    'x-csrf-token': '1Xg2eGp5Gq7wsPkKQsbBGdtqgVr0om4W',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'referer': 'https://yuba.douyu.com/p/995429941549108124',
    'authority': 'yuba.douyu.com',
    'cookie': 'dy_did=a17b4ab25c54986f6433ea9b00061501; acf_yb_did=a17b4ab25c54986f6433ea9b00061501; _ga=GA1.2.898345405.1546830910; smidV2=20181222155555157e437e6e4f57b560a3855ffdf9aace007e26097861818f0; Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1548322847,1548651214,1549120614,1550039793; wan_auth37wan=300a20ad8d19UVSZHIdMGTa2ECOjqaCg2gzvHEO4GUig23sy5OV99pi%2FuoirglUS1FyIfc1Aw2TNEAaFTn6yr9zqKClIrVVMVVZQySt98WbOmBKVVw; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1548345770,1548650379,1550564629; _gid=GA1.2.1834890484.1550656523; _gat_gtag_UA_128072138_1=1; acf_yb_t=1Xg2eGp5Gq7wsPkKQsbBGdtqgVr0om4W; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1550656532; acf_yb_auth=8a70bc400803da5685c6cc8e7272d3c99bc35c82; acf_yb_new_uid=qy70WlRPJAXG; acf_yb_uid=39581553; Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1550656550',
}

params = (
    ('timestamp', '0.5236318728209359'),
)

data = {
  'repost': '0',
  'content': '<p>777</p>',
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
