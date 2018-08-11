#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
实现对request的存储，这里实现了三种方式的queue：
FIFO的SpiderQueue，SpiderPriorityQueue，以及LIFI的SpiderStack。默认使用的是第二中
'''


from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.http import Request

try:
    import cPickle as pickle
except ImportError:
    import pickle


class Base(object):
    """Per-spider queue/stack base class 队列的基类"""

    def __init__(self, server, spider, key, queue_name):
        """Initialize per-spider redis queue.  初始化redis的队列

        Parameters:参数
            server -- redis connection  redis的实例
            spider -- spider instance   爬虫实例
            key -- key for this queue (e.g. "%(spider)s:queue")
        """
        self.server = server
        self.spider = spider
        self.key = key % {'spider': queue_name}

    def _encode_request(self, request):
        """Encode a request object"""  #序列化request
        return pickle.dumps(request_to_dict(request, self.spider), protocol=-1)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""  #反序列化request
        return request_from_dict(pickle.loads(encoded_request), self.spider)

    def __len__(self):
        """Return the length of the queue"""  #返回队列的长度
        raise NotImplementedError

    def push(self, request):
        """Push a request"""  #存一个请求
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""   #弹出一个请求
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""  #清楚队列
        self.server.delete(self.key)


class SpiderQueue(Base):
    """Per-spider FIFO queue"""  #先进先出

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""  #push
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)


class SpiderPriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""  #用redis的排序来决定哪个先出

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        pairs = {data: -request.priority}
        self.server.zadd(self.key, **pairs)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])


class SpiderSimpleQueue(Base):
    """ url + callback """

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        # if 'info' not in request.url:
        #     self.server.lpush(self.key, request.url[16:])
        # else:
        self.server.lpush(self.key, request.url)


    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            url = self.server.brpop(self.key, timeout=timeout)
            if isinstance(url, tuple):
                url = url[1]
        else:
            url = self.server.rpop(self.key)
        print('queue_url:',url)
        if url:
            url = url.decode()
            try:
                if "/follow" in url or "/fans" in url:
                    cb = getattr(self.spider, "parse_relationship")  #返回这个方法
                    #base_url = 'https://weibo.c'
                elif "/profile" in url:
                    cb = getattr(self.spider, "parse_tweets")
                    #base_url = 'https://weibo.c'
                elif "/info" in url:
                    #base_url = 'https://weibo.c'
                    cb = getattr(self.spider, "parse_information")
                else:
                    raise ValueError("Method not found in: %s( URL:%s )" % (self.spider, url))


                return Request(url="{}".format(url), callback=cb)
            except AttributeError:
                raise ValueError("Method not found in: %s( URL:%s )" % (self.spider, url))


class SpiderStack(Base):
    """Per-spider stack"""

    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


__all__ = ['SpiderQueue', 'SpiderPriorityQueue', 'SpiderSimpleQueue', 'SpiderStack']

