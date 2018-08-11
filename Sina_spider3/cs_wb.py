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


# import redis
#
#
# r = redis.Redis(host='localhost',port='6379',db=0)
#
# html = r.get('SinaSpider:dupefilter0')
# print htm

from selenium import webdriver
import time
import json

browser = webdriver.Chrome()#(desired_capabilities=dcap)
browser.get("https://passport.weibo.cn/signin/login")
try:
    time.sleep(2)

    #browser.save_screenshot("aa.png")
    username = browser.find_element_by_xpath('//*[@id="loginName"]')
    username.clear()
    username.send_keys('13548612815')
    time.sleep(5)
    psd = browser.find_element_by_xpath('//*[@id="loginPassword"]')
    psd.clear()
    psd.send_keys('whw199508157276')
    time.sleep(5)
    commit = browser.find_element_by_xpath('//*[@id="loginAction"]')
    commit.click()
    time.sleep(5)

    cookie = {}
    print(browser.title)
    #print browser.get_cookies()
    if "微博" in browser.title.decode('utf-8'):
        for elem in browser.get_cookies():
            cookie[elem["name"]] = elem["value"]
        #logger.warning("Get Cookie Success!( Account:%s )" % account)
    print(cookie)
except Exception as e:
    #logger.warning("Failed %s!" % account)
    print(e)

finally:
    browser.quit()
