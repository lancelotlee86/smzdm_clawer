# encoding=utf8
# !/usr/bin/python3

from time import sleep

import requests
from bs4 import BeautifulSoup

from models import Item

from pymongo import  MongoClient
client = MongoClient()
db = client.shopping_clawer
smzdm = db.smzdm_clawer

def send_email(item):
    pass


while 1:
    # do requests
    headers = {
        'Host': 'faxian.smzdm.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2792.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://www.smzdm.com/youhui/',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cookie': 'smzdm_user_source=5CC2C9B68005E5628FAC9A52A0825EDE; _ga=GA1.2.1567107262.1466862324; smzdm_user_view=95DD778EB3BD2F6279E146C290B0F21C; PHPSESSID=j926ihj0rek6dgi87hce27r6q0; home_header_small_slideStuff_cookie=2; __jsluid=c22aecabb9f7d71dfb6a2f4937b95b6a; wt3_eid=%3B999768690672041%7C2146824491500653413%232146824495300832389; wt3_sid=%3B999768690672041; Hm_lvt_9b7ac3d38f30fe89ff0b8a0546904e58=1466862322,1468245033; Hm_lpvt_9b7ac3d38f30fe89ff0b8a0546904e58=1468246800; count_i=1',
        'DNT': '1'
    }
    url = "http://faxian.smzdm.com/"

    r = requests.get(url=url, headers=headers)
    print('request sent')
    r.encoding = 'utf-8'

    soup = BeautifulSoup(r.text.replace("\r", "").replace("\n", "").replace("\t", ""))

    ul_container = soup.select('.leftWrap.discovery_list')[0]  # 获取包含着所有物品的那个<ul>标签
    all_items = ul_container.select('li')

    for item in all_items:      # 循环中，每一个item都代表<ul>标签下的一个<li>标签
        this_item = Item()      # 实例化一个新的Item对象
        this_item.articleid = item['articleid']     # 获取该<li>标签的 articleid 属性
        this_item.link = item.select_one('.picBox')['href']     # 获取链接
        this_item.title = item.select_one('.itemName').select_one('.black').text    # 获取这个商品的标题
        this_item.price = item.select_one('.itemName').select_one('.red').text      # 获取这个商品的价格
        this_item.date = item.select_one('.time').text
        # 还有一些要补充，稍后再说
        if not smzdm.find_one({'articleid': this_item.articleid}):  # 记录没有在数据库中
            send_email(this_item)       # 将这条记录邮件出去
            print(this_item.to_dict())
            smzdm.insert_one(this_item.to_dict())   # 将这条记录存放在数据库中
    sleep(5)