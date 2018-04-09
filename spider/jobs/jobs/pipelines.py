# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jobs.mongodb import Mongodb

class LagouPipeline(object):
    def __init__(self):
        self.db = Mongodb('127.0.0.1', 27017, 'job_info', 'jobs')

    def process_item(self, item, spider):
        self.db.save(item)
        return item
