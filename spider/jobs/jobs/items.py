# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    title = scrapy.Field()
    city = scrapy.Field()
    salary = scrapy.Field()
    company = scrapy.Field()
    tags = scrapy.Field()
    education = scrapy.Field()
    experience = scrapy.Field()
    site = scrapy.Field()
    tech = scrapy.Field()
    tech_stack = scrapy.Field()
    desc = scrapy.Field()
