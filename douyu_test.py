
import os
import re
import pytz
import time
import socket
import struct
import pymongo
import requests
from threading import Thread
from datetime import datetime

SERVER_ADDR = ('223.111.12.101', 12601)
mongodb_uri = 'mongodb://127.0.0.1:27017/douyu'
mongodb_client = pymongo.MongoClient(os.environ.get('MONGODB_URL', mongodb_uri))


def get_today():
    today = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y_%m_%d')
    return today


def get_now():
    today = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y_%m_%d: %H:%M:%S')
    return today


def get_room_info(uid):
    """根据主播的uid(房间url上的), 获取纯数字的room_id和主播中文名.
    :param uid: str.
    :return room_id: str, 房间id.
            name: str, 主播中文名.
    """
    url = 'http://www.douyu.com/{}'.format(uid)
    r = requests.get(url)
    name = re.findall('<h1>(.*)</h1>', r.text)[0]
    return uid, name


def send_msg(cfd, msg):
    """
    发给斗鱼服务器所有的包都得加上消息头, 格式见斗鱼弹幕手册.
    :param cfd:
    :param msg: str.
    """
    content = msg.encode()
    # 消息长度, 这里加8而不是加12.所以实际tcp数据部分长度会比斗鱼协议头长度大4
    length = len(content) + 8
    # 689代表客户端向服务器发送的数据, 690代表服务器向客户端发送的数据
    code = 689
    head = struct.pack('i', length) + struct.pack('i', length) + struct.pack('i', code)
    if isinstance(cfd, socket.socket):
        cfd.sendall(head + content)
    else:
        print('wrong type: {}'.format(cfd))


def init(uid):
    """向服务器发送相应数据包, 准备接收弹幕.
    :param uid: str, 主播的uid(房间url上的).
    :return cfd: 套接字描述符.
    """
    room_id, name = get_room_info(uid)
    cfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    host = socket.gethostbyname("openbarrage.douyutv.com")
    port = 8601
    cfd.connect((host, port))
    # loginreq中的req指requests, 还需要紧接着发下面一个包, 服务器会返回loginres
    msg_login = 'type@=loginreq/username@=/password@=/roomid@={}/\x00'.format(room_id)
    send_msg(cfd, msg_login)
    print('你进入了{}的直播间，房间id是{}'.format(name, room_id))
    # 直觉认为这里暂停一秒比较好
    time.sleep(1)
    # gid=-9999代表接收海量弹幕, 发完下面这个包, 服务器才会向客户端发送弹幕
    msg_join = 'type@=joingroup/rid@={}/gid@=-9999/\x00'.format(room_id)
    send_msg(cfd, msg_join)
    return cfd


def get_gift_list(room_id):
    gift_list = dict()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    url = 'http://open.douyucdn.cn/api/RoomApi/room/' + str(room_id)
    room_info = requests.get(url, headers=headers).json()['data']
    for each in room_info['gift']:
        gift_list[each['id']] = each['name']
        print('{}, {}'.format(each['id'], each['name']))
    return gift_list


def get_dm(cfd, rid, gift_list):
    """接受服务器消息, 并提取弹幕信息."""
    pattern = re.compile(b'type@=chatmsg/.+?/uid@=(.+?)/nn@=(.+?)/txt@=(.+?)/.+?/level@=(.+?)/.+?')
    gift_msg = re.compile(b'type@=dgb/.+?/gfid@=(.+?)/.+?/nn@=(.+?)/.+?/gfcnt@=(.+?)/.+?')  # 礼物
    while True:
        # 接收的包有可能被分割, 需要把它们重新合并起来, 不然信息可能会缺失
        buffer = b''
        while True:
            recv_data = cfd.recv(4096)
            buffer += recv_data
            if recv_data.endswith(b'\x00'):
                break

        for uid, nn, txt, level in pattern.findall(buffer):
            # 斗鱼有些表情会引发unicode编码错误
            # `error='replace'`, 把其替换成'?'
            print('[lv.{:0<2}][{}]: {}'.format(level.decode(), nn.decode(), txt.decode(errors='replace').strip()))
            db = mongodb_client.get_database()['{}_{}'.format(rid, get_today())]
            db.insert_one(
                {
                    'uid': uid.decode(), 'type': 'danmu',
                    'level': level.decode(), 'name': nn.decode(), 'text': txt.decode(errors='replace').strip(),
                    'time': get_now()}
            )

        for gfid, name, gfcnt in gift_msg.findall(buffer):
            # print('{} 赠送 {} 个 {}'.format(name.decode(), gfcnt.decode(), gfid.decode()))
            db = mongodb_client.get_database()['{}_{}'.format(rid, get_today())]
            db.insert_one({
                'name': name.decode(), 'type': 'gift',
                'gift_count': gfcnt.decode(), 'gift_id': gfid.decode(),
                'time': get_now()})


def keep_live(cfd):
    while True:
        print('维持心跳: {}'.format(get_now()))
        time.sleep(40)
        msg_keep = 'type@=mrkl/\x00'
        send_msg(cfd, msg_keep)


def main(rid):
    cfd = init(rid)
    gift_list = get_gift_list(rid)
    t = Thread(target=keep_live, args=(cfd,), daemon=True)
    t.start()

    t2 = Thread(target=get_dm, args=(cfd, rid, gift_list))
    t2.start()
    t2.join()


if __name__ == '__main__':
    # main('208114')
    room_list = ['208114', '4537144']
    for rid in room_list:
        t = Thread(target=main, args=(rid,))
        # t.setDaemon(True)
        t.start()
