# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import time

from fake_useragent.fake import UserAgent
from scrapy import signals


# useful for handling different item types with a single interface


class CrawlsinaSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawlsinaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = UserAgent(use_cache_server=False)
        request.headers['User-Agent'] = ua.random


class RandomDelayMiddleware(object):
    def process_request(self, request, spider):
        delay = random.random()
        time.sleep(delay)  # sleep random seconds [0, 1)


class RandomWeiboCookiesMiddleware(object):
    def __init__(self):
        self.weibocookies = [
            '_T_WM=73216813430; SUB=_2A25N1dY8DeRhGeNH7loS9CjFzjiIHXVvOfp0rDV6PUJbktB-LWPAkW1NSolvpXYRikdO1lDJY8EpakB2BUQq3FkC; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W58Q-F-Mc1.iJhdP.YGh2am5NHD95Qf1K-Re0Bc1K-XWs4DqcjGIGDrehzESntt; SSOLoginState=1624352364',
            '_T_WM=8e237735a15831d7b6e4a2711f2a05f8; SUB=_2A25N1cHaDeRhGeNI6VcV8S7NyTWIHXVvOe-SrDV6PUJbktAKLULRkW1NSJodLV4c843IZgTepQZ-qXL4A7jb9TJE; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWeZKTcdflPnmhdXyNMW.m75NHD95QfSozfSh27eKz4Ws4Dqc_xi--fiKy2iK.Ni--fi-zpi-zpi--Xi-i8iKn0i--fi-88i-2Ei--NiKLWiKnXi--fi-isiKn0i--ciKn0iKnfi--ciK.Ni-2fi--Ri-88i-z7; SSOLoginState=1624355210',
            'SUB=_2A25NuCrqDeRhGeFI6VMR8y3KyjyIHXVvQrairDV6PUJbktB-LRCnkW1NfVc-G4mdP-YsIqxaxIqOzmFm1koP7GpS; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5ZY9IE3wozNIYdkjS0QJ-G5JpX5KzhUgL.FoMceo27e0eceK52dJLoIpRLxKqL1--L1KMLxKqL1--L1KMLxKqL1-BLBo5peK2t; SSOLoginState=1622956730; _T_WM=97383355022'
        ]

    def process_request(self, request, spider):
        if spider.name == 'weibo':
            weibocookie = random.choice(self.weibocookies)
            request.cookies = {i.split('=')[0]: i.split('=')[1] for i in weibocookie.split('; ')}
