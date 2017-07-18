#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Date    : 2017/6/26 0026 16:49
# @Author  : wangxian (908686161@qq.com)

# from selenium import webdriver
# import time

# browser = webdriver.Chrome()

# browser.get('https://passport.weibo.cn/signin/login')
# time.sleep(2)
# username = browser.find_element_by_xpath('//*[@id="loginName"]')
# username.clear()
# time.sleep(2)
# username.send_keys('13548612815')
# time.sleep(2)
# password = browser.find_element_by_xpath('//*[@id="loginPassword"]')
# time.sleep(2)
# password.clear()
# time.sleep(2)

# password.send_keys('whw199508157276')
# time.sleep(2)
# time.sleep(2)
# browser.find_element_by_xpath('//*[@id="loginAction"]').click()
# time.sleep(10)
# browser.quit()


import redis


r = redis.Redis(host='localhost',port='6379',db=0
html = r.get('SinaSpider:dupefilter0')
print htm