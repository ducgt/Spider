# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboCommentItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    name = scrapy.Field()
    activity_id = scrapy.Field()
    activity_text = scrapy.Field()
    comment_user_id = scrapy.Field()
    comment_user_name = scrapy.Field()
    comment_time = scrapy.Field()
    comment_text = scrapy.Field()

