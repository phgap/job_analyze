import scrapy
from jobs.items import JobItem
import random

class ZhilianSpider(scrapy.Spider):
    name = "zhilian"

    start_urls = []

    def parse(self, response):
        pass

    def get_jobs(self, resp):
        return resp.css('.s_position_list .item_con_list li')

    def get_id(self, job):
        return job.css('.position_link::attr(href)').extract_first()

    def get_title(self, job):
        return job.css('.position_link h2::text').extract_first()

    def get_city(self, job):
        return job.css('.position_link span.add em::text').extract_first()

    def get_salary(self, job):
        return job.css('.p_bot span.money::text').extract_first()

    def get_company(self, job):
        return job.css('.company_name a::text').extract_first()

    def get_tags(self, job):
        return job.css('.list_item_bot .li_b_l span::text').extract()

    def get_education(self, job):
        pass

    def get_experience(self, job):
        pass
