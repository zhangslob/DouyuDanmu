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
    'x-csrf-token': '6VpG4UPcgq4mx2cDPCmn5W9UMkOM2VzB',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'referer': 'https://yuba.douyu.com/p/580027761547043070',
    'authority': 'yuba.douyu.com',
    'cookie': 'dy_did=a17b4ab25c54986f6433ea9b00061501; acf_yb_did=a17b4ab25c54986f6433ea9b00061501; _ga=GA1.2.898345405.1546830910; _dys_lastPageCode=page_yuba_detail,page_yuba_detail; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1545465128,1546395515,1546839422; smidV2=20181222155555157e437e6e4f57b560a3855ffdf9aace007e26097861818f0; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1547175937; Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1547087949,1547089028,1547100500,1547175944; _gid=GA1.2.644898675.1547446717; acf_yb_auth=ff5b0def5969878f652de1d2c8b40309403b4ac1; acf_yb_new_uid=qy70WlRPJAXG; acf_yb_uid=39581553; acf_yb_t=6VpG4UPcgq4mx2cDPCmn5W9UMkOM2VzB; _dys_refer_action_code=init_page_yuba_detail; Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1547446728',
}

params = (
    ('timestamp', '0.8552529192809504'),
)

data = {
  'repost': '0',
  'content': '<p>1</p>',
  'pid': '580027761547043070',
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
        time.sleep(30)
