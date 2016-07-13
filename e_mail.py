import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime

def send_email():
    print("sending email..." + str(datetime.datetime.now()))
    sender = 'lishenzhi@yeah.net'
    receiver = '823990768@qq.com'
    subject = 'python email test'
    smtpserver = 'smtp.yeah.net'
    username = 'lishenzhi@yeah.net'
    password = 'lishenzhi1214'

    items = [
        {
            "price": "$34", "description": None,
            "link": "http://www.smzdm.com/p/6232982/",
            "articleid": "2_6232982",
            "title": "9码起：ANDREW MARC Dorchester Crepe Chukka 男士休闲鞋",
            "date": None
        },
        {
            "price": "1518日元",
            "description": None,
            "link": "http://www.smzdm.com/p/6233309/",
            "articleid": "2_6233309",
            "title": "pigeon 贝亲 婴儿日常护理套装",
            "date": None}
    ]
    content = ''
    count = 1
    for item in items:
        text = '{}. ({})  {} {}\n'.format(count, item['date'],item['title'], item['link'])
        content = content + text
        count += 1

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver

    smtp = smtplib.SMTP()
    smtp.connect('smtp.yeah.net')
    smtp.login(username, password)
    #smtp.send_message(msg, from_addr=sender, to_addrs=receiver)
    smtp.sendmail(sender, [receiver], msg.as_string())
    smtp.quit()

send_email()