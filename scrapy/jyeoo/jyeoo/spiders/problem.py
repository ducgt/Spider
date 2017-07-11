# -*- coding: utf-8 -*-
import scrapy
import furl
from random import uniform
import re
from jyeoo.items import JyeooItem


class ProblemSpider(scrapy.Spider):
    name = "problem"
    allowed_domains = ["jyeoo.com"]
    start_urls = (
        'http://www.jyeoo.com/',
    )

    def parse(self, response):
        problem = {}
        report = {}
        sub_cat_list = response.css('#cont > div.sub-group > ul > li > div.sub-list > ul > li')
        for one in sub_cat_list:
            title = one.css('a::attr(title)').extract()
            link = one.css('a::attr(href)').extract()
            try:
                problem[title[0]] = link[0]
                report[title[1]] = link[1]
            except IndexError:
                pass

        for k, v in problem.items():
            self.logger.debug('{} {}'.format(k, v))
            if 'jeyoo' in v:
                pass
            else:
                yield scrapy.Request(url='http://www.jyeoo.com' + v + '?f=1', callback=self.get_sub_cat,
                                     meta={'cat_title': k, 'cat_url': v})
                break

    def get_sub_cat(self, response):
        k = response.meta.get('cat_title')
        v = response.meta.get('cat_url')
        click_list = {}
        tmp_list = response.css('table.degree > tr> td > ul > li > a')
        for one in tmp_list:
            onclick = one.css('::attr(onclick)').extract_first()
            t = onclick[3:5]
            n = onclick.split(',')[-1][:-1]
            if t not in click_list:
                click_list[t] = [n]
            else:
                click_list[t].append(n)
        # self.logger.info(click_list)
        v = v.replace('/search', '')
        url = 'http://www.jyeoo.com' + v + '/partialcategory?a=undefined&q=1&f=1&r=' + str(uniform(0, 1))
        yield scrapy.Request(url=url, callback=self.get_partialcategory,
                             meta={'cat_title': k, 'cat_url': v, 'click_list': click_list})

    def get_partialcategory(self, response):
        cat_title = response.meta.get('cat_title')
        cat_link = response.meta.get('cat_url')
        click_list = response.meta.get('click_list')
        self.logger.debug('{} {}'.format(cat_title, cat_link))
        pk_list = {}
        cat_list = response.css('#ulTree > li > ul > li > ul > li > a')
        for one in cat_list:
            pk = one.css('a::attr(pk)').extract_first()
            title = one.css('a::attr(title)').extract_first()
            pk_list[pk] = title
        ct = click_list['CT'][1:]
        dg = click_list['DG'][1:]
        fg = click_list['FG'][1:]
        so = click_list['SO'][1:]
        # self.logger.debug(pk_list)
        # self.logger.debug('ct {} dg {} fg {} so {}'.format(ct, dg, fg, so))
        for pk_one, title in pk_list.items():
            for ct_one in ct:
                for dg_one in dg:
                    for fg_one in fg:
                        for so_one in so:
                            new_url = furl.furl('http://www.jyeoo.com' + cat_link + '/partialques')
                            parms = {'q': pk_one, 'f': 1, 'ct': ct_one, 'dg': dg_one, 'fg': fg_one, 'po': 0, 'pd': 0,
                                     'pi': 1,
                                     'lbs': 0, 'so': so_one, 'so2': 0, 'r': 0}
                            new_url.add(args=parms)
                            word = cat_link.replace('/ques', '').replace('/', '')
                            self.logger.debug(word)
                            yield scrapy.Request(url=new_url.url, callback=self.parse_page,
                                                 meta={'cat_title': cat_title, 'cookie': True, 'word': word,
                                                       'parms': parms, 'sub_cat_title': pk_list[pk_one]})
                            break
                        break
                    break
                break
            break

    def parse_page(self, response):
        cat_title = response.meta.get('cat_title')
        sub_cat_title = response.meta.get('sub_cat_title')
        self.logger.debug('cat title {} sub cat title {} url {}'.format(cat_title, sub_cat_title, response.url))
        # a:nth-child(1)::attr(href)
        detail_list = response.css('div.ques-list > ul > li > span.fieldtip > a::attr(href)').extract()
        next_page = response.css('body > div.page > div > a.next::attr(href)').extract_first()
        self.logger.debug('next page {}'.format(next_page))
        self.logger.debug(detail_list)
        if detail_list:
            for one in detail_list:
                if 'http' in one:
                    yield scrapy.Request(url=one, callback=self.parse_detail)
                break
        if next_page:
            try:
                page_number = re.findall('[\d]*,this', next_page)[0]
                page_number = page_number.split(',')[0]
            except IndexError as e:
                self.logger.warning('{} {}'.format(next_page, e))
            self.logger.debug(page_number)
            next_url = furl.furl(response.url)
            next_url.args['pi'] = 2
            yield scrapy.Request(url=next_url.url, callback=self.parse_page, meta={'cat_title': cat_title,
                                                                                   'sub_cat_title': sub_cat_title})

    def parse_detail(self, response):
        content = response.css('fieldset.quesborder > div.pt1').extract()
        option = response.css('fieldset.quesborder > div.pt2 > table > tbody > tr > td > label').extract()
        # 考点
        point = response.css('fieldset.quesborder > div.pt3 > a').extract()
        # 【专题】
        topic = response.css('fieldset.quesborder > div.pt4').extract()
        # 【分析】
        analyise = response.css('fieldset.quesborder > div.pt5').extract()
        answer = response.css('fieldset.quesborder > div.pt6').extract()
        comment = response.css('fieldset.quesborder > div.pt7').extract()
        teacher = response.css('fieldset.quesborder > div.pt9 > span:nth-child(2)').extract()
        self.logger.debug(
            'content {} \n option {}\n ponit {}\n analyise {}\n answer {}\n comment {}\n　teacher{}\n'.format(content,
                                                                                                             option,
                                                                                                             point,
                                                                                                             topic,
                                                                                                             analyise,
                                                                                                             answer,
                                                                                                             comment,
                                                                                                             teacher))
        yield JyeooItem({'content': content, 'option': option, 'point': point, 'topic': topic, 'analyise': analyise,
                         'answer': answer, 'comment': comment, 'teacher': teacher})


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
