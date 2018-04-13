# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import json
import random
import re
from jobs.selenium.selenium_downloader import SeleniumDownloader
from scrapy.http import Request
from scrapy.http import HtmlResponse


class JobsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    def __init__(self):
        self.next_page_selector = {
            "lagou": '.pager_container a:last-of-type'
        }

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

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            if isinstance(i, Request):
                i = self.process_request(i)
            yield i

    def process_request(self, request):
        print("=======================spider middleware process_request: url:", request.url)
        if re.match(r'https://www.lagou.com/zhaopin/[^/]*/\d+/', request.url) is not None:
            request.meta['next_page_selector'] = self.next_page_selector["lagou"]
        else:
            request.meta['next_page_selector'] = None
        return request

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
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


class LagouDownloaderMiddleware(object):
    def __init__(self):
        self.selenimu = SeleniumDownloader()

    def __del__(self):
        self.selenimu.close()

    def process_request(self, request, spider):
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        if self.is_next_page(request):
            body = self.selenimu.next_page_by_click(request.meta['next_page_selector'])
            return HtmlResponse(request.url,
                                body=body,
                                encoding='utf-8',
                                request=request)
        elif self.is_lagou_index(request.url):
            body = self.selenimu.load(request.url)
            return HtmlResponse(request.url,
                                body=body,
                                encoding='utf-8',
                                request=request)
        else:
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

    def is_lagou_index(self, url):
        # https://www.lagou.com/zhaopin/Java/?labelWords=label
        result = re.match(r"https://www.lagou.com/zhaopin/[^/]*/\??\D*", url)
        return result is not None

    def is_next_page(self, request):
        return request.meta.get('next_page_selector') is not None
