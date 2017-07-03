# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["thepaper.cn"]
    start_urls = (
        'http://www.thepaper.cn',
    )

    def parse(self, response):
        news_list = response.css('div.news_li')
        for one in news_list:
            url = one.css('h2 > a::attr(href)').extract_first()
            title = one.css('h2 > a::text').extract_first()
            if url:
                yield scrapy.Request(url='http://www.thepaper.cn/' + url, callback=self.parse_news)

        pageindex = response.css('div[pageindex]::attr(pageindex)').extract_first()
        last_time = response.css('div[pageindex]::attr(lasttime)').extract_first()
        self.logger.info('pageindex {} last_time {}'.format(pageindex, last_time))
        base_url = response.meta.get('base_url')
        if base_url:
            pass
        else:
            script = response.css('#indexMasonry > script::text').extract_first()
            base_url = re.findall('nodeids=.*pageidx=', script)[0]
        true_url = 'http://www.thepaper.cn/load_chosen.jsp?{}{}&lastTime={}'.format(base_url, pageindex, last_time)
        self.logger.info(true_url)
        yield scrapy.Request(url=true_url, callback=self.parse, meta={'base_url': base_url})

    def parse_news(self, response):
        title = response.css('head > title::text').extract_first()
        source = response.css('div.newscontent > div.news_about > p:nth-child(1)::text').extract_first()
        time = response.css('div.newscontent > div.news_about > p:nth-child(2)::text').extract_first()
        text = response.css('div.main_lt > div.newscontent > div.news_txt').extract_first()
        self.logger.debug('{} {} {} {}'.format(title, source, time, text))


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
