# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JyeooItem(scrapy.Item):
    content = scrapy.Field()
    option = scrapy.Field()
    point = scrapy.Field()
    topic = scrapy.Field()
    analyise = scrapy.Field()
    answer = scrapy.Field()
    comment = scrapy.Field()
    teacher = scrapy.Field()
