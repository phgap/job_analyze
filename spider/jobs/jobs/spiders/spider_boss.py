import scrapy
from jobs.items import JobItem
import random


class BossSpider(scrapy.Spider):
    name = "boss"

    start_urls = ['https://www.zhipin.com']

    def parse(self, response):
        print("============================URL", response.url)
        job_menu = response.css('div.job-menu')
        if job_menu is not None:
            for link_request in self.get_job_category(response):
                yield link_request
        else:
            jobs = self.get_jobs(response)
            # TODO: 创建工作ITEM
            # TODO: 添加下一页链接

    def get_job_category(self, resp):
        # 第一个为IT互联网分类，此处可以将slice，将所有job分类取出
        cates = resp.css('div.job-menu .menu-sub ul')[0:1]
        for cate in cates:
            links = cate.css('li div.text a::attr(href)').extract()
            for link in links:
                link = resp.urljoin(link)
                yield scrapy.Request(link, callback=self.parse)

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
