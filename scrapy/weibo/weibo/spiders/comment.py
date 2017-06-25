# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from weibo.items import WeiboCommentItem


class CommentSpider(scrapy.Spider):
    name = "comment"
    iterate_enable = False
    allowed_domains = ["weibo.cn"]

    def start_requests(self):
        self.iterate_enable = self.settings.getbool('ITERATE_ENABLE')
        user_id_list = [1195242865]
        for uid in user_id_list:
            yield Request(url='https://m.weibo.cn/p/100505{}'.format(uid), meta={'uid': uid}, callback=self.parse)

    def parse(self, response):
        uid = response.meta.get('uid')
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=100505{}'.format(uid, uid)
        yield Request(url=url, meta={'uid': uid}, callback=self.parse_profile)

    def parse_profile(self, response):
        raw_data = json.loads(response.text)
        name = raw_data['userInfo']['screen_name']
        uid = response.meta.get('uid')
        activity_url = 'https://m.weibo.cn/api/container/getIndex?type=uid' \
                       '&value={}&containerid=107603{}'.format(uid, uid)
        self.logger.debug('name = {},id={}'.format(name, uid))
        yield Request(url=activity_url, meta={'uid': uid, 'name': name, 'page': 1}, callback=self.parse_activity)

    def parse_activity(self, response):
        uid = response.meta.get('uid')
        name = response.meta.get('name')
        now_page = response.meta.get('page')
        activity_data = json.loads(response.text)
        for one in activity_data['cards']:
            activity_id = one['mblog']['id']
            activity_text = one['mblog']['text']
            comment_url = 'https://m.weibo.cn/api/comments/show?id={}&page=1'.format(activity_id)
            yield Request(url=comment_url, callback=self.parse_comment,
                          meta={'uid': uid, 'name': name, 'activity_id': activity_id, 'activity_text': activity_text,
                                'page': 1})
        max_page = activity_data['cardlistInfo']['page']
        if now_page < max_page:
            now_page += 1
            activity_url = 'https://m.weibo.cn/api/container/getIndex?type=uid' \
                           '&value={}&containerid=107603{}&page={}'.format(uid, uid, now_page)
            self.logger.info('activity page number = {}'.format(now_page))
            yield Request(url=activity_url, meta={'uid': uid, 'name': name, 'page': now_page},
                          callback=self.parse_activity)

    def parse_comment(self, response):
        uid = response.meta.get('uid')
        name = response.meta.get('name')
        now_page = response.meta.get('page')
        activity_id = response.meta.get('activity_id')
        activity_text = response.meta.get('activity_text')
        raw_data = json.loads(response.text)
        try:
            data = raw_data['data']
        except KeyError:
            self.logger.info(raw_data)
            data = None
        if data:
            for one in data:
                comment_user_id = one['user']['id']
                comment_user_name = one['user']['screen_name']
                comment_time = one['created_at']
                comment_text = one['text']
                yield WeiboCommentItem({'uid': uid, 'name': name, 'activity_id': activity_id,
                                        'activity_text': activity_text, 'comment_user_id': comment_user_id,
                                        'comment_user_name': comment_user_name,
                                        'comment_time': comment_time, 'comment_text': comment_text})
                if self.iterate_enable:
                    yield Request(url='https://m.weibo.cn/p/100505{}'.format(comment_user_id),
                                  meta={'uid': comment_user_id}, callback=self.parse)
        try:
            max_page = raw_data['max']
            total_number = raw_data['total_number']
        except Exception as e:
            self.logger.info(e)
            max_page = now_page
            total_number = 0
            self.logger.debug('now more comment,now page = {},total number={}'.format(now_page, total_number))
        if now_page < max_page:
            now_page += 1
            comment_url = 'https://m.weibo.cn/api/comments/show?id={}&page={}'.format(activity_id, now_page)
            yield Request(url=comment_url, callback=self.parse_comment,
                          meta={'uid': uid, 'name': name, 'activity_id': activity_id, 'activity_text': activity_text,
                                'page': now_page})


if __name__ == '__main__':
    from scrapy.cmdline import execute

    execute()
