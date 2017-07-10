# -*- coding: utf-8 -*-
import scrapy
import furl
from random import uniform


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
        self.logger.info(click_list)
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
        self.logger.debug(pk_list)
        self.logger.debug('ct {} dg {} fg {} so {}'.format(ct, dg, fg, so))
        for pk_one, title in pk_list.items():
            for ct_one in ct:
                for dg_one in dg:
                    for fg_one in fg:
                        for so_one in so:
                            new_url = furl.furl('http://www.jyeoo.com' + cat_link)
                            parms = {'q': pk_one, 'f': 1, 'ct': ct_one, 'dg': dg_one, 'fg': fg_one, 'po': 0, 'pd': 0,
                                     'pi': 1,
                                     'lbs': 0, 'so': so_one, 'so2': 0, 'r': 0}
                            new_url.add(args=parms)
                            self.logger.debug(new_url.url)
                break
            break

if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
