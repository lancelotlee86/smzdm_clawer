# encoding=utf8
# !/usr/bin/python3

import datetime
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import threading
from pymongo import  MongoClient
from models import Item
try:
    import config_instance
except ImportError:
    import config


# setup mongodb
client = MongoClient()
db = client.shopping_clawer
smzdm = db.smzdm_clawer


def send_email(items_to_email):
    """
    一个辅助方法，接收一个Item对象的列表，并提取我们需要的数据，格式化后发送邮件出去
    :param items_to_email: 装着Item对象的列表
    :return: None
    """
    print("sending email..." + str(datetime.datetime.now()))
    sender = config_instance.SENDER
    receiver = config_instance.RECEIVER
    subject = config_instance.SUBJECT
    smtpserver = config_instance.SMTPSERVER
    username = config_instance.USERNAME
    password = config_instance.PASSWORD

    body = ''
    count = 1
    for item in items_to_email:
        text = '{}. ({})  {} {}\n'.format(count, item.date,item.title, item.link)
        body = body + text
        count += 1

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, [receiver], msg.as_string())
    smtp.quit()


class Clawer:
    headers = None
    url = None
    reponse = None


class SmzdmClawer(Clawer):
    def __init__(self):
        self.headers = {
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
        self.url = "http://faxian.smzdm.com/"

    def open_url(self, url=None):
        """
        打开给定或默认的URL，用Requests库请求
        :param url: str
        :return: None或requests对象
        """
        if url:
            self.url = url
        # 试着访问，如果超时或者别的原因，则返回空
        try:
            r = requests.get(url=self.url, headers=self.headers, timeout=2)
            if r.status_code != 200:
                return None
        except:
            return None

        print('request sent')
        r.encoding = 'utf-8'
        return r

    @staticmethod
    def close_response(response):
        response.close()

    @staticmethod
    def parase(response):
        """
        接收requests库请求后的响应对象，清理HTML，用BeautifulSoup库解析
        :param response: requests库的响应对象
        :return: beautifulsoup解析html后的对象
        """
        soup = BeautifulSoup(response.text.replace("\r", "").replace("\n", "").replace("\t", ""))
        return soup

    @staticmethod
    def get_items(soup):
        """
        接收 parase() 方法传递的 beautifulsoup 对象，得到包含着Item对象的列表
        :param soup: beautifulsoup 对象
        :return: 包含着Item对象的列表
        """
        ul_container = soup.select('.leftWrap.discovery_list')[0]  # 获取包含着所有物品的那个<ul>标签
        all_items = ul_container.select('li')
        items = []      # 一个装着Item对象的列表
        for item in all_items:  # 循环中，每一个item都代表<ul>标签下的一个<li>标签
            this_item = Item()  # 实例化一个新的Item对象
            this_item.articleid = item['articleid']  # 获取该<li>标签的 articleid 属性
            this_item.link = item.select_one('.picBox')['href']  # 获取链接
            this_item.title = item.select_one('.itemName').select_one('.black').text  # 获取这个商品的标题
            this_item.price = item.select_one('.itemName').select_one('.red').text  # 获取这个商品的价格
            this_item.date = item.select_one('.time').text

            items.append(this_item)     # 添加当前的Item对象到items列表
        return items

    @staticmethod
    def exist(item):
        """
        检查给定的item是否存在在数据库中
        :param item: Item对象
        :return: Boolean
        """
        if smzdm.find_one({'articleid': item.articleid}):
            return True     # 如果该记录已存在
        else:
            return False


def main():
    """
    main()做一下几个事，
    1. 2秒后开启新的Threading运行main()---->>
    2. 访问页面并用beautifulsoup库解析，得到这一时间点的所有页面上的items---->>
    3. 遍历items，不在数据库中的，添加到数据库，并且添加到items_to_mail[]---->>
    4. 调用send_email()将items_to_mail[]发送出去
    :return: None
    """
    threading.Timer(2, main).start()    # 每次开始main函数时，新开一个递归的线程，以此实现每2秒请求一次
    now = datetime.datetime.now()
    print('starting a new threading: ' + str(threading.current_thread().ident) + ' @ ' + str(now))
    print('total threads alive count: ' + str(threading.active_count()))

    # 下面4行做的工作：访问页面-->解析页面-->得到item对象的列表
    smzdm_clawer = SmzdmClawer()
    response_page = smzdm_clawer.open_url(url="http://faxian.smzdm.com/")
    if not response_page:   # 如果返回的页面是None，则跳过这一轮请求
        print('页面请求失败...')
        return
    parsed_page = smzdm_clawer.parase(response_page)
    items_in_smzdm = smzdm_clawer.get_items(parsed_page)  # 得到了所有的item对象，在一个列表item_in_smzdm中
    smzdm_clawer.close_response(response_page)

    # 检查页面中每一条记录是否已存在，如不存在，说明是新的记录，通过邮件发送并存储在数据库中
    items_to_email = []
    for item in items_in_smzdm:
        if not smzdm.find_one({'articleid': item.articleid}):  # 记录没有在数据库中
            items_to_email.append(item)  # 将这条记录添加到待邮列表中
            print('new item found, sending email...')
            print(item.to_dict())
            smzdm.insert_one(item.to_dict())  # 将这条记录存放在数据库中
    if items_to_email:  # 将这次请求找到的items发送出去
        send_email(items_to_email)

    print('after process threading' + str(threading.current_thread().ident))

    return

if __name__ == '__main__':
    main()
