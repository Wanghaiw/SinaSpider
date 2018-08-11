#!/usr/bin/emv python
# -*- coding:utf-8 -*-

'''
负责执行requst的去重，实现的很有技巧性，使用redis的set数据结构。但是注意scheduler并不使用其中用于在这个模块中实现的dupefilter键做request的调度，而是使用queue.py模块中实现的queue。
当request不重复时，将其存入到queue中，调度时将其弹出。
'''

import time
import re
import logging
from scrapy.dupefilters import BaseDupeFilter



from . import connection
#

class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplication filter"""  #基于Redis的请求过滤器

    def __init__(self, server, key):
        """Initialize duplication filter  初始化复制过滤器

        Parameters  参数
        ----------
        server : Redis instance  redis实例
        key : str
            Where to store fingerprints
        """
        self.server = server
        self.key = key

    @classmethod
    def from_settings(cls, settings):
        server = connection.from_settings_filter(settings)
        key = "dupefilter:%s" % int(time.time())
        return cls(server, key)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        uid = re.findall('(\d+)/info', request.url) #匹配用户的id
        if uid:
            uid = int(uid[0])
            isExist = self.server.getbit(self.key + str(uid / 4000000000), uid % 4000000000)
            if isExist == 1:
                return True
            else:
                self.server.setbit(self.key + str(uid / 4000000000), uid % 4000000000, 1)
                return False

    def close(self, reason):
        """Delete data on close. Called by scrapy's scheduler"""
        self.clear()

    def clear(self):
        """Clears fingerprints data"""
        self.server.delete(self.key)


#
#
# logger = logging.getLogger(__name__)
#
#
# # TODO: Rename class to RedisDupeFilter.
# class RFPDupeFilter(BaseDupeFilter):
#     """Redis-based request duplicates filter.
#
#     This class can also be used with default Scrapy's scheduler.
#
#     """
#
#     logger = logger
#
#     def __init__(self, server, key, debug=False):
#         """Initialize the duplicates filter.
#
#         Parameters
#         ----------
#         server : redis.StrictRedis
#             The redis server instance.
#         key : str
#             Redis key Where to store fingerprints.
#         debug : bool, optional
#             Whether to log filtered requests.
#
#         """
#         self.server = server
#         self.key = key
#         self.debug = debug
#         self.logdupes = True
#
#     @classmethod
#     def from_settings(cls, settings):
#         """Returns an instance from given settings.
#
#         This uses by default the key ``dupefilter:<timestamp>``. When using the
#         ``scrapy_redis.scheduler.Scheduler`` class, this method is not used as
#         it needs to pass the spider name in the key.
#
#         Parameters
#         ----------
#         settings : scrapy.settings.Settings
#
#         Returns
#         -------
#         RFPDupeFilter
#             A RFPDupeFilter instance.
#
#
#         """
#         server = connection.from_settings_filter(settings)
#         # XXX: This creates one-time key. needed to support to use this
#         # class as standalone dupefilter with scrapy's default scheduler
#         # if scrapy passes spider on open() method this wouldn't be needed
#         # TODO: Use SCRAPY_JOB env as default and fallback to timestamp.
#         key = defaults.DUPEFILTER_KEY % {'timestamp': int(time.time())}
#         debug = settings.getbool('DUPEFILTER_DEBUG')
#         return cls(server, key=key, debug=debug)
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         """Returns instance from crawler.
#
#         Parameters
#         ----------
#         crawler : scrapy.crawler.Crawler
#
#         Returns
#         -------
#         RFPDupeFilter
#             Instance of RFPDupeFilter.
#
#         """
#         return cls.from_settings(crawler.settings)
#
#     def request_seen(self, request):
#         """Returns True if request was already seen.
#
#         Parameters
#         ----------
#         request : scrapy.http.Request
#
#         Returns
#         -------
#         bool
#
#         """
#         fp = self.request_fingerprint(request)
#         # This returns the number of values added, zero if already exists.
#         added = self.server.sadd(self.key, fp)
#         return added == 0
#
#     def request_fingerprint(self, request):
#         """Returns a fingerprint for a given request.
#
#         Parameters
#         ----------
#         request : scrapy.http.Request
#
#         Returns
#         -------
#         str
#
#         """
#         return request_fingerprint(request)
#
#     def close(self, reason=''):
#         """Delete data on close. Called by Scrapy's scheduler.
#
#         Parameters
#         ----------
#         reason : str, optional
#
#         """
#         self.clear()
#
#     def clear(self):
#         """Clears fingerprints data."""
#         self.server.delete(self.key)
#
#     def log(self, request, spider):
#         """Logs given request.
#
#         Parameters
#         ----------
#         request : scrapy.http.Request
#         spider : scrapy.spiders.Spider
#
#         """
#         if self.debug:
#             msg = "Filtered duplicate request: %(request)s"
#             self.logger.debug(msg, {'request': request}, extra={'spider': spider})
#         elif self.logdupes:
#             msg = ("Filtered duplicate request %(request)s"
#                    " - no more duplicates will be shown"
#                    " (see DUPEFILTER_DEBUG to show all duplicates)")
#             self.logger.debug(msg, {'request': request}, extra={'spider': spider})
#            self.logdupes = False
#
