#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Date    : 2017/7/21 0021 23:11
# @Author  : wangxian (908686161@qq.com)
import pymongo

clinet = pymongo.MongoClient("localhost", 27017)
db = clinet["Sina"]
Information = db["Information"]
Tweets = db["Tweets"]
Relationships = db["Relationships"]