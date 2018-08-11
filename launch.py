#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Date    : 2018/3/3 0003 22:30
# @Author  : wangxian (908686161@qq.com)

# from scrapy import cmdline
#
# cmdline.execute("scrapy crawl SinaSpider".split())


import pymongo


client = pymongo.MongoClient('172.16.172.122',20717)
db = client['SS']
Information = db["Information"]

print(Information.find_one())