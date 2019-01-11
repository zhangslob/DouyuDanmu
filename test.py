#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: test.py 
@time: 2019/01/10
@desc: 
"""
import time
import requests

headers = {
    'origin': 'https://yuba.douyu.com',
    'accept-encoding': 'gzip, deflate, br',
    'x-csrf-token': 'Q848WTsnRUXPuyVdIkBy6GgjBCVcOwPc',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'referer': 'https://yuba.douyu.com/p/580027761547043070',
    'authority': 'yuba.douyu.com',
    'cookie': 'dy_did=a17b4ab25c54986f6433ea9b00061501; acf_yb_did=a17b4ab25c54986f6433ea9b00061501; _ga=GA1.2.898345405.1546830910; _gid=GA1.2.338468931.1546830910; _dys_lastPageCode=page_yuba_detail,page_yuba_detail; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1545465128,1546395515,1546839422; smidV2=20181222155555157e437e6e4f57b560a3855ffdf9aace007e26097861818f0; acf_yb_auth=37fd9d803866bbae31a6a6618762f7440409ee67; acf_yb_new_uid=qy70WlRPJAXG; acf_yb_uid=39581553; wan_auth37wan=524fdde5d01d%2F6ZML9eyEoA1tBKy4AMK%2FXxfiMJbylOvT5b7lgO71ix58RJr8WD9SCpNCP0EzliM0jW6ILWqUs016mT9wrJlOzA5mM1MBGzEe9plSQ; acf_yb_t=Q848WTsnRUXPuyVdIkBy6GgjBCVcOwPc; _dys_refer_action_code=init_page_yuba_detail; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1547089023; _gat_gtag_UA_128072138_1=1; Hm_lvt_e0374aeb9ac41bee98043654e36ad504=1547023228,1547031807,1547087949,1547089028; Hm_lpvt_e0374aeb9ac41bee98043654e36ad504=1547089032',
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


def run():
    try:
        response = requests.post('https://yuba.douyu.com/ybapi/answer/comment', headers=headers, params=params, data=data)
        print(response.json()['status_code'])
        print(time.time())
    except:
        print('retry')
        time.sleep(30)
        return run()


if __name__ == '__main__':
    while True:
        run()
        time.sleep(30)
