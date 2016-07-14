### smzdm clawer

	Python3.x+
	MongoDB

用来抓取[什么值得买：发现频道](http://www.faxian.smzdm.com)实时发布的物品，并且通过邮件发送出来。

####整体思路：
1.  用[Requests](http://www.python-requests.org/en/master/)库打开www.faxian.smzdm.com页面，得到HTML代码
2.  用[beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)库解析HTML，得到这一时间点的所有页面上的items
3. 遍历items，不在数据库中的，添加到数据库，并且添加到items_to_email[]
4. 调用send_email()将items_to_mail[]发送出去
5.  将上述过程每2秒钟执行一次（为保证http请求和发送邮件时不被阻塞，需要做异步。本想用Python3.4标准库的[asyncio](https://docs.python.org/3.5/library/asyncio.html)来做异步，结果看了半天还是不会用，所以暂时先用了Threading这个路子）


代码结构和功能的封装可能做的不太合理，请见谅。我会多看看开源项目学习学习。

（请先配置config.py里的内容）