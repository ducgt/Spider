# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.linkextractors import LinkExtractor
import re


class CommentSpider(scrapy.Spider):
    name = "comment"
    allowed_domains = ["tmall.com"]
    start_urls = ['https://www.tmall.com/']

    def parse(self, response):
        raw_data_str = response.css('#J_defaultData::text').extract_first()
        raw_data_json = json.loads(raw_data_str)
        tmp_category = raw_data_json['mockPage']['100']['categoryMainLines']
        category_dict = self.process_cat(tmp_category)
        # self.logger.debug(category_dict)
        for one in category_dict.values():
            host = one.replace('//', '').split('/')[0]
            # self.logger.debug('host {}'.format(host))
            yield scrapy.Request(url='https:' + one, callback=self.parse_category,
                                 meta={'Host': host, 'headers': True})
            break

    def parse_category(self, response):
        raw_data = response.css('#J_TmFushiNavCate > ul > li:nth-child(1) > ul').extract_first()
        link_list = re.findall('href="((//list.tmall.com/)([^"]+))"', raw_data)
        for one in link_list:
            self.logger.debug(one[0])
            yield scrapy.Request(url='https:' + one[0], callback=self.parse_every_category,
                                 meta={'Host': 'list.tmall.com', 'headers': True})
            break

    def parse_every_category(self, response):
        self.logger.info(response.url)
        next_page = response.css(
            '#content > div.main > div.ui-page > div > b.ui-page-num > a.ui-page-next::attr(href)').extract_first()
        next_page = 'https://list.tmall.com/search_product.htm' + next_page
        yield scrapy.Request(url=next_page, callback=self.parse_every_category,
                             meta={'Host': 'list.tmall.com', 'headers': True})

    @staticmethod
    def process_cat(category):
        res = {}
        for one in category:
            if 'action1' in one and 'title1' in one:
                tmp = {one['title1']: one['action1']}
                if tmp:
                    res.update(tmp)
            if 'action2' in one and 'title2' in one:
                tmp = {one['title2']: one['action2']}
                if tmp:
                    res.update(tmp)
            if 'action3' in one and 'title3' in one:
                tmp = {one['title3']: one['action3']}
                if tmp:
                    res.update(tmp)
        return res


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
