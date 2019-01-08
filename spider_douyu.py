#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: spider_douyu.py 
@time: 2019/01/04
@desc:
    房间详细信息：http://open.douyucdn.cn/api/RoomApi/room/4537144 + https://www.douyu.com/betard/4537144
    主播标签：https://www.douyu.com/wgapi/live/anchor/tag/top3?room_id=4537144&cate2=1
    直播工会：https://www.douyu.com/ztCache/club/getanchorclubstatus?roomid=4537144
    礼物列表：https://webconf.douyucdn.cn/resource/common/gift/flash/gift_effect.json + https://webconf.douyucdn.cn/resource/common/prop_gift_list/prop_gift_config.json
    房间礼物：https://webconf.douyucdn.cn/resource/common/gift/gift_template/684.json
    等级信息：POST：https://www.douyu.com/anchor_level/getLevelInfo，Data：roomId: 4537144
    主播关注：https://yuba.douyu.com/wbapi/web/user/detail/194337263?space=1
    主播排行：https://www.douyu.com/column_rank_list/getAnchorRankList?cate_id=1&room_id=208114&uid=9468763

    未知可能有用：https://accp.douyucdn.cn/resource/common/activity/gma_config.json

    斗鱼在送出火箭、飞机之后会有全局推送，可以监听某一个房间，计算该房间的一天礼物价值，和模型计算出来的数据进行对比。
    都有弹幕监控我也有写过，代码在`https://github.com/zhangslob/awesome_crawl/blob/master/douyu_danmu/douyu_websocket_client.py`

    # TODO: 增加异常处理，如果出现异常直接重试该请求
"""

import json
import scrapy
import pymysql


class RoomItem(scrapy.Item):
    id = scrapy.Field()             # 房间ID
    owner_name = scrapy.Field()     # 主播名字
    online = scrapy.Field()         # 原人气字段，现在与热度值同步
    hn = scrapy.Field()             # 在线热度值
    uid = scrapy.Field()            # 用户ID
    level = scrapy.Field()          # 用户等级
    upgrade_exp = scrapy.Field()    # 还需xx经验值到达下一级
    min_exp = scrapy.Field()        # 未知可能有用
    experience = scrapy.Field()     # 未知可能有用
    keep_exp = scrapy.Field()       # 保级任务经验值
    exp_distance = scrapy.Field()   # 还缺xx完成保级任务
    end_time = scrapy.Field()       # 上次直播时间
    next_level = scrapy.Field()     # 下一等级
    progress = scrapy.Field()       # 升级比例：37.8%
    first_cate = scrapy.Field()     # 第一分类
    second_cate = scrapy.Field()    # 第二分类
    third_cate = scrapy.Field()     # 第三分类
    user_level = scrapy.Field()     # 用户等级
    fans_num = scrapy.Field()       # 用户粉丝（房间订阅数）
    fu_num = scrapy.Field()         # 用户关注数


class DouYuSpider(scrapy.Spider):

    name = 'douyu'
    allowed_domains = ['douyu.com']
    room_url = 'https://m.douyu.com/api/room/list?page={}&type='

    api_url = 'http://open.douyucdn.cn/api/RoomApi/room/{}'
    betard_url = 'https://www.douyu.com/betard/{}'
    user_url = 'https://yuba.douyu.com/wbapi/web/user/detail/{}'

    start_urls = [room_url.format(1)]

    headers = {
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://www.douyu.com',
        'authority': 'www.douyu.com',
        'x-requested-with': 'XMLHttpRequest', }

    custom_settings = {
        'CONCURRENT_REQUESTS': 64,
        'DOWNLOAD_DELAY': 0,
        'COOKIES_ENABLED': False,
        'ROBOTSTXT_OBEY': False,
        'RETRY_TIMES': 15,
        'DEFAULT_REQUEST_HEADERS': {
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) '
                          'AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://m.douyu.com/',
            'authority': 'm.douyu.com',
            'x-requested-with': 'XMLHttpRequest',
        },
        # 'ITEM_PIPELINES': {
        #     '': 301,
        # },
        'DOWNLOADER_MIDDLEWARES': {
            "scrapy_zs.utils.middlewares_.ProxyMiddleware": 520
        },
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_TIMEOUT': 10
    }

    def parse(self, response):
        """
        抓取所有正在直播的房间ID
        :param response:
        :return:
        """
        page = json.loads(response.text)
        for i in page['data']['list']:
            yield scrapy.Request(
                url=self.api_url.format(i['rid']),
                headers=self.headers,
                callback=self.parse_api_data, dont_filter=True
            )

        # 如果是第一页，处理翻页
        if response.url == self.room_url.format(1):
            page_count = page['data']['pageCount']
            self.logger.info('all page count: {}'.format(page_count))
            for page in range(2, page_count+1):
                yield scrapy.Request(url=self.room_url.format(page))

    def parse_api_data(self, response):
        """
        http://open.douyucdn.cn/api/RoomApi/room/4537144
        API 中的房间信息
        :param response:
        :return:
        """
        rid = response.url.split("/")[-1]
        room = dict()
        try:
            resp_api = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            response.request.dont_filter = True
            yield response.request
            self.logger.info('retry {}'.format(response.url))
            return

        room['id'] = int(rid)
        room['owner_name'] = resp_api['data']['owner_name']
        room['online'] = resp_api['data']['online']
        room['hn'] = resp_api['data']['hn']

        yield scrapy.Request(
            self.betard_url.format(rid), headers=self.headers,
            callback=self.parse_betard_data, meta={'room': room}
        )

    def parse_betard_data(self, response):
        """
        https://www.douyu.com/betard/4537144
        抓取等级信息
        :param response: 4537144
        :return:
        """
        room = response.meta['room']
        resp_betard = json.loads(response.text)

        room['uid'] = resp_betard['room']['owner_uid']
        room['level'] = resp_betard['room']['levelInfo']['level']
        room['upgrade_exp'] = resp_betard['room']['levelInfo']['upgrade_exp']
        room['min_exp'] = resp_betard['room']['levelInfo']['min_exp']
        room['experience'] = resp_betard['room']['levelInfo']['experience']
        room['keep_exp'] = resp_betard['room']['levelInfo']['keep_exp']
        room['exp_distance'] = resp_betard['room']['levelInfo']['exp_distance']
        room['end_time'] = resp_betard['room']['levelInfo']['end_time']
        room['next_level'] = resp_betard['room']['levelInfo']['next_level']
        room['progress'] = resp_betard['room']['levelInfo']['progress']
        room['first_cate'] = resp_betard['column']['cate_name']
        room['second_cate'] = resp_betard['game']['tag_name']

        if 'child_cate' in resp_betard.keys():
            if isinstance(resp_betard['child_cate'], dict):
                room['third_cate'] = resp_betard['child_cate']['name']
            elif isinstance(resp_betard['child_cate'], list):
                room['third_cate'] = '暂无'
        else:
            room['third_cate'] = '暂无'

        yield scrapy.Request(
            self.user_url.format(room['uid']), headers=self.headers,
            callback=self.parse_user_data, meta={'room': room}
        )

    def parse_user_data(self, response):
        """
        https://yuba.douyu.com/wbapi/web/user/detail/194337263
        抓取用户关注数据（订阅数）
        :param response:
        :return:
        """
        room = response.meta['room']

        try:
            resp_user = json.loads(response.text)
            room['user_level'] = resp_user['data']['level']
            room['fans_num'] = resp_user['data']['fans_num']
            room['fu_num'] = resp_user['data']['fu_num']

        except KeyError:
            response.request.dont_filter = True
            yield response.request
            self.logger.info('retry {}'.format(response.url))
            return

        # self.logger.info(room['id'])
        # insert_to_mysql(room)

        yield RoomItem(room)


def create_table():
    """
    在mysql创建表
    :return:
    """
    sql = """
        CREATE TABLE IF NOT EXISTS `douyu` (
          `id` int(255) NOT NULL,
          `owner_name` varchar(255) DEFAULT NULL,
          `online` int(255) DEFAULT NULL,
          `hn` int(255) DEFAULT NULL,
          `uid` int(11) DEFAULT NULL,
          `level` varchar(255) DEFAULT NULL,
          `upgrade_exp` varchar(255) DEFAULT NULL,
          `min_exp` int(255) DEFAULT NULL,
          `experience` float(255,0) DEFAULT NULL,
          `keep_exp` varchar(255) DEFAULT NULL,
          `exp_distance` varchar(255) DEFAULT NULL,
          `end_time` varchar(255) DEFAULT NULL,
          `next_level` int(255) DEFAULT NULL,
          `progress` float(255,0) DEFAULT NULL,
          `first_cate` varchar(255) DEFAULT NULL,
          `second_cate` varchar(255) DEFAULT NULL,
          `third_cate` varchar(255) DEFAULT NULL,
          `user_level` int(255) DEFAULT NULL,
          `fans_num` int(11) DEFAULT NULL,
          `fu_num` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
    db = pymysql.connect("localhost", "root", "123456", "spiders")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print('{}, {}'.format(e, sql))
        db.rollback()


def insert_to_mysql(data):
    """
    数据插入mysql
    :param data: dict
    :return:
    """
    db = pymysql.connect("localhost", "root", "123456", "spiders")
    cursor = db.cursor()

    sql = """INSERT INTO douyu (
    id, owner_name, online, hn, uid, level, upgrade_exp, min_exp, experience,
    keep_exp, exp_distance, end_time, next_level, progress, first_cate, second_cate,
    third_cate, user_level, fans_num, fu_num
    ) VALUES ({}, '{}', {}, {}, {}, '{}', '{}', {}, {}, '{}', '{}', '{}', {},
    {}, '{}', '{}', '{}', {}, {}, {})""".format(
            data['id'], str(data['owner_name']), data['online'], data['hn'], data['uid'],
            str(data['level']), str(data['upgrade_exp']), data['min_exp'], data['experience'],
            str(data['keep_exp']), str(data['exp_distance']), str(data['end_time']), data['next_level'],
            data['progress'], str(data['first_cate']), str(data['second_cate']), str(data['third_cate']),
            data['user_level'], data['fans_num'], data['fu_num']
        )

    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print('{}, {}'.format(e, sql))
        db.rollback()
