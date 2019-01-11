#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: douyu_yuba_post.py 
@time: 2019/01/08
@desc: 
"""

import os
import requests
import pymongo
from zs_factor import getip

env = os.environ
# topic = env.get("ZS_FACTOR_TOPIC", "dailiyun")
group = env.get("ZS_FACTOR_GROUP")
num = env.get("ZS_FACTOR_NUM", 20)

mongodb_uri = 'mongodb://127.0.0.1:27017/douyu'
mongodb_client = pymongo.MongoClient(os.environ.get('MONGODB_URL', mongodb_uri))
db = mongodb_client.get_database()['guanren_yuba']
db.create_index('pid', unique=True)

headers = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'user-agent': 'android',
    'accept': 'application/json, text/plain, */*',
    'referer': 'https://yubam.douyu.com/group/3299915',
    'authority': 'yubam.douyu.com',
}


def get_ip(topic):
    for _ in range(15):
        proxy = getip(topic, group=group, num=num)
        if proxy:
            break
    return {'http': proxy, 'https': proxy}


class YuBa(object):

    def __init__(self, tid):
        self.tid = tid

    @staticmethod
    def download(url, *args, **kwargs):
        print(url)
        return requests.get(url, headers=headers, timeout=10,
                            proxies=get_ip('daoliyun'), *args, **kwargs).json()

    @staticmethod
    def save_data(json_text):
        try:
            db.insert_many(json_text, ordered=False)
        except pymongo.errors.DuplicateKeyError:
            pass
        except pymongo.errors.BulkWriteError:
            pass

    @staticmethod
    def get_last_params(json_text):
        last_time = json_text['data']['itemList'][-1]['time']
        last_qid = json_text['data']['itemList'][-1]['pid']
        return last_time, last_qid

    def get_first_page(self):
        response = self.download('https://yubam.douyu.com/ybapi/topic/mPostList?tid=3299915')
        self.save_data(response['data']['itemList'])

        last_time, last_qid = self.get_last_params(response)
        return last_time, last_qid

    def main(self):
        last_time, last_qid = self.get_first_page()

        url = 'https://yubam.douyu.com/ybapi/topic/mPostList?tid={}&last_time={}&last_qid={}'
        running = True
        while running:
            response = self.download(url.format(self.tid, last_time, last_qid))
            if response['status'] == 'ok':
                self.save_data(response['data']['itemList'])
                last_time, last_qid = self.get_last_params(response)
            else:
                running = False


if __name__ == '__main__':
    YuBa('3299915').main()

