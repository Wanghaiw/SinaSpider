#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Date    : 2018/3/3 0003 22:30
# @Author  : wangxian (908686161@qq.com)

import os
import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logger = logging.getLogger(__name__)
dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过

dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

"""
    输入你的微博账号和密码，可去淘宝买，一元5个。
    建议买几十个，实际生产建议100+，微博反爬得厉害，太频繁了会出现302转移。
"""
myWeiBo = [
    ('13548612815', 'whw199508157276')
    
]
IDENTIFY = 1

def getCookie(account, password):
    """ 获取一个账号的Cookie """
    browser = webdriver.Chrome()#(desired_capabilities=dcap)
    try:
        browser.get("https://passport.weibo.cn/signin/login")
        time.sleep(1)

        #browser.save_screenshot("aa.png")
        username = browser.find_element_by_xpath('//*[@id="loginName"]')
        username.clear()
        username.send_keys(account)
        time.sleep(5)
        psd = browser.find_element_by_xpath('//*[@id="loginPassword"]')
        psd.clear()
        psd.send_keys(password)
        time.sleep(5)
        commit = browser.find_element_by_xpath('//*[@id="loginAction"]')
        commit.click()
        time.sleep(10)

        cookie = {}
        print(browser.title)
        if "微博" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning("Get Cookie Success!( Account:%s )" % account)
        return json.dumps(cookie)
    except Exception as e:
        logger.warning("Failed %s!" % account)
        print(e)
        return ""
    finally:
        browser.quit()



def initCookie(rconn, spiderName):
    """ 获取所有账号的Cookies，存入Redis。如果Redis已有该账号的Cookie，则不再获取。 """
    for weibo in myWeiBo:
        print(weibo[0],'=========')
        print(rconn.get("%s:Cookies:%s--%s" % (spiderName, weibo[0], weibo[1])))  # 获取cookie的值
        print(rconn.keys())
        if rconn.get("%s:Cookies:%s--%s" % (spiderName, weibo[0], weibo[1])) is None:  # 'SinaSpider:Cookies:账号--密码'，为None即不存在。

            cookie = getCookie(weibo[0], weibo[1])
            if len(cookie) > 0:
                rconn.set("%s:Cookies:%s--%s" % (spiderName, weibo[0], weibo[1]), cookie)
    cookieNum = "".join([key.decode() for key in rconn.keys()]).count("SinaSpider:Cookies")
    logger.warning("The num of the cookies is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        os.system("pause")


def updateCookie(accountText, rconn, spiderName):
    """ 更新一个账号的Cookie """
    account = accountText.split("--")[0]
    password = accountText.split("--")[1]
    cookie = getCookie(account, password)
    if len(cookie) > 0:
        logger.warning("The cookie of %s has been updated successfully!" % account)
        rconn.set("%s:Cookies:%s" % (spiderName, accountText), cookie)
    else:
        logger.warning("The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText, rconn, spiderName)


def removeCookie(accountText, rconn, spiderName):
    """ 删除某个账号的Cookie """
    rconn.delete("%s:Cookies:%s" % (spiderName, accountText))
    cookieNum = "".join(rconn.keys()).count("SinaSpider:Cookies")
    logger.warning("The num of the cookies left is %s" % cookieNum)
    if cookieNum == 0:
        logger.warning('Stopping...')
        os.system("pause")


