import scrapy
from jobs.items import JobItem


class LagouSpider(scrapy.Spider):
    name = "lagou"

    start_urls = [
        'https://www.lagou.com/zhaopin/Java/',
    ]

    def __init__(self):
        super(LagouSpider, self).__init__()
        self.urls = [
            'https://www.lagou.com/zhaopin/Python/',
            'https://www.lagou.com/zhaopin/PHP/',
            'https://www.lagou.com/zhaopin/.NET/',
            'https://www.lagou.com/zhaopin/C%23/',
            'https://www.lagou.com/zhaopin/C%2B%2B/',
            'https://www.lagou.com/zhaopin/C/',
            'https://www.lagou.com/zhaopin/VB/',
            'https://www.lagou.com/zhaopin/Delphi/',
            'https://www.lagou.com/zhaopin/Perl/',
            'https://www.lagou.com/zhaopin/Ruby/',
            'https://www.lagou.com/zhaopin/Hadoop/',
            'https://www.lagou.com/zhaopin/Node.js/',
            'https://www.lagou.com/zhaopin/shujuwajue/',
            'https://www.lagou.com/zhaopin/ziranyuyanchuli/',
            'https://www.lagou.com/zhaopin/sousuosuanfa/',
            'https://www.lagou.com/zhaopin/jingzhuntuijian/',
            'https://www.lagou.com/zhaopin/quanzhangongchengshi/',
            'https://www.lagou.com/zhaopin/go/',
            'https://www.lagou.com/zhaopin/asp/',
            'https://www.lagou.com/zhaopin/shell/',
        ]

    def parse(self, response):
        # extract job info
        jobs = self.get_jobs(response)
        """
            _id = scrapy.Field()
            title = scrapy.Field()
            city = scrapy.Field()
            salary = scrapy.Field()
            company = scrapy.Field()
            tags = scrapy.Field()
            education = scrapy.Field()
            experience = scrapy.Field()
            site = scrapy.Field()
            desc = scrapy.Field()
        """
        for job in jobs:
            item = JobItem()
            item["_id"] = self.get_id(job)
            item["title"] = self.get_title(job)
            item["city"] = self.get_city(job)
            item["salary"] = self.get_salary(job)
            item["tags"] = self.get_tags(job)
            item["site"] = "www.lagou.com"
            item["company"] = self.get_company(job)
            item["education"] = self.get_education(job)
            item["experience"] = self.get_experience(job)
            print('===================experience:', self.get_experience(job))
            item["desc"] = self.get_desc(job)
            yield item

        # follow links
        next_page = response.css('div.pager_container a:last-child::attr(href)').extract_first()
        if next_page is not None and next_page != "javascript:;":
            next_page = response.urljoin(next_page)
            # print('==============================next_page', next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        elif next_page == "javascript:;":
            try:
                next_page = self.urls.pop()
                # print('==============================next_page[category]', next_page)
                yield scrapy.Request(next_page, callback=self.parse)
            except IndexError as e:
                print('except:', e)
        else:
            pass

    def get_jobs(self, resp):
        return resp.css('.s_position_list .item_con_list li')

    def get_id(self, job):
        return job.css('.position_link::attr(href)').extract_first()

    def get_title(self, job):
        return job.css('.position_link h3::text').extract_first()

    def get_city(self, job):
        return job.css('.position_link span.add em::text').extract_first()

    def get_salary(self, job):
        return job.css('.p_bot span.money::text').extract_first()

    def get_company(self, job):
        return job.css('.company_name a::text').extract_first()

    def get_tags(self, job):
        return job.css('.list_item_bot .li_b_l span::text').extract()

    def get_education(self, job):
        return job.css('.p_bot div.li_b_l').re(r"<!--<i></i>-->(.*)")[0].split("/")[1].strip()

    def get_experience(self, job):
        return job.css('.p_bot div.li_b_l').re(r"<!--<i></i>-->(.*)")[0].split("/")[0].strip()

    def get_desc(self, job):
        # TODO:
        return None
