# encoding=utf8
# !/usr/bin/python3

class Item:
    articleid = None
    title = None
    price = None
    link = None
    date = None
    description = None

    def to_dict(self):
        item = {
            'articleid': self.articleid,
            'title': self.title,
            'price': self.price,
            'link': self.link,
            'date': self.date,
            'description': self.description
        }
        return item