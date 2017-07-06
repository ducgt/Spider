# -*- coding: utf-8 -*-
import scrapy
import re
from pengpai.items import NewsItem
import time
import random
import pyreBloom
import json

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["thepaper.cn"]
    start_urls = (
        'http://www.thepaper.cn',
        'http://www.thepaper.cn/channel_26916',
        'http://www.thepaper.cn/channel_25950',
    )
    my_key = 'pengpai_news_BloomFilter'.encode('utf8')
    my_host = '127.0.0.1'.encode('utf8')
    my_passwd = 'poluo123'.encode('utf8')
    filter = pyreBloom.PyreBloom(my_key, 200000, 0.01, host=my_host, password=my_passwd)
    request_count = 0
    request_url = []

    def parse(self, response):
        # 视频
        if '26916' in response.url:
            res = self.process_video(response)
        # 时事
        elif '25950' in response.url or '25462' in response.url:
            res = self.process_text(response)
        # 精选
        else:
            res = self.process_main(response)
        url_list = res['url_list']
        for one in url_list:
            tmp = self.to_bytes(one)
            if tmp not in self.filter:
                self.filter.add(tmp)
                self.logger.info('news url {}'.format(one))
                yield scrapy.Request(url='http://www.thepaper.cn/' + one, callback=self.parse_news)
        next_page = res['next_page']
        info = res['info']
        if next_page:
            self.logger.info('next page {}'.format(next_page))
            yield scrapy.Request(url=next_page, callback=self.parse, meta={'info': info})

    @staticmethod
    def process_video(response):
        video_list = response.css('li.video_news')
        url_list = []
        for one in video_list:
            url = one.css('a::attr(href)').extract_first()
            if url:
                url_list.append(url)

        page_idx = response.meta.get('info')
        if page_idx:
            page_idx += 1
        else:
            page_idx = 2
        next_page = 'http://www.thepaper.cn/load_video_chosen.jsp?channelID=26916&pageidx={}'.format(page_idx)
        if page_idx > 2 and not url_list:
            next_page = None
        return {'url_list': url_list, 'next_page': next_page, 'info': page_idx}

    @staticmethod
    def process_text(response):
        url_list = []
        news_list = response.css('div.news_li')
        for one in news_list:
            url = one.css('h2 > a::attr(href)').extract_first()
            if url:
                url_list.append(url)

        page_idx = response.meta.get('info')
        if page_idx:
            page_idx += 1
            next_page = 'http://www.thepaper.cn/load_index.jsp?nodeids=25462,25488,25489,25490,25423,25426,25424,' \
                        '25463,25491,25428,25464,25425,25429,25481,25430,25678,25427,25422,25487,25634,25635,25600,' \
                        '&topCids=1724670,1724901,1724631&pageidx={}&lastTime={}'.format(page_idx, int(
                time.time() * 1000) - random.randint(1000, 1200))
            if not url_list:
                next_page = None
        else:
            page_idx = 1
            next_page = 'http://www.thepaper.cn/channel_masonry.jsp?channelID=25950&_={}'.format(
                int(time.time() * 1000) - random.randint(1000, 1200))
        return {'url_list': url_list, 'next_page': next_page, 'info': page_idx}

    @staticmethod
    def process_main(response):
        url_list = []
        news_list = response.css('div.news_li')
        for one in news_list:
            url = one.css('h2 > a::attr(href)').extract_first()
            if url:
                url_list.append(url)

        pageindex = response.css('div[pageindex]::attr(pageindex)').extract_first()
        last_time = response.css('div[pageindex]::attr(lasttime)').extract_first()
        base_url = response.meta.get('info')
        if base_url:
            pass
        else:
            script = response.css('#indexMasonry > script::text').extract_first()
            base_url = re.findall('nodeids=.*pageidx=', script)[0]
        if not pageindex:
            next_page = None
        else:
            next_page = 'http://www.thepaper.cn/load_chosen.jsp?{}{}&lastTime={}'.format(base_url, pageindex, last_time)
        return {'url_list': url_list, 'next_page': next_page, 'info': base_url}

    @staticmethod
    def to_bytes(s):
        if isinstance(s, str):
            return s.encode('utf8')
        elif isinstance(s, bytes):
            return s
        else:
            raise TypeError

    def parse_news(self, response):
        self.request_count += 1
        
        title = response.css('head > title::text').extract_first()
        self.request_url.append({'url':response.url,'title':title})
        video = response.css('div.video_news_detail.video_w1200 > video > source::attr(src)').extract_first()
        if video:
            text = response.xpath('/html/body/div[3]/div[2]/div/div[2]/p/text()').extract_first().strip()
            source = response.css('div.video_txt_l > div > div.oriBox > span::text').extract_first()
            time = response.css('div.video_txt_l > div > div.video_info > span:nth-child(3)::text').extract_first()

        else:
            source = response.css('div.newscontent > div.news_about > p:nth-child(1)::text').extract_first()
            time = response.css('div.newscontent > div.news_about > p:nth-child(2)::text').extract_first()
            text = response.css('div.main_lt > div.newscontent > div.news_txt').extract_first()
        res = NewsItem({'title': title, 'source': source, 'time': time, 'text': text, 'video': video})
        self.logger.debug(res)
        yield res

    def closed(self, reason):
        self.logger.info('spider {} closed {}'.format(self.name, reason))
        with open('res_{}.json'.format(int(time.time())),'w') as fobj:
            json.dump({'count':self.request_count,'url':self.request_url}, fobj)


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
