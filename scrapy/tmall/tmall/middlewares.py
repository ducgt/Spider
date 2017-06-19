import logging as logger
from tmall.agents import AGENTS
import random


class CustomNormalMiddleware(object):
    def __init__(self):
        self.cookies = {}

    def process_request(self, request, spider):
        try:
            headers_disable = request.meta.get('headers_disable')
        except KeyError:
            headers_disable = False

        if not headers_disable:
            request.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            request.headers['Accept-Encoding'] = 'gzip, deflate, sdch, br'
            request.headers['Accept-Language'] = 'zh-CN,zh;q=0.8,zh-TW;q=0.6'
            request.headers['Connection'] = 'keep-alive'
            request.headers['Host'] = 'www.tmall.com'
            request.headers['cache-control'] = 'max-age=0'
            request.headers['upgrade-insecure-requests'] = 1
            request.headers['DNT'] = 1
            logger.debug('reqeust headers{}'.format(request.headers))
        try:
            headers_enable = request.meta.get('headers')
        except Exception as e:
            logger.info(e)
            headers_enable = False
        if headers_enable:
            try:
                request.headers['Host'] = request.meta.get('Host')
            except Exception as e:
                logger.info(e)
        if self.cookies:
            request.cookies = self.cookies

    def process_response(self, request, response, spider):
        if response.status == 302:
            try:
                new_meta = {}
                if 'Set-Cookie' in response.headers:
                    logger.debug(response.headers)
                    self.cookies = self.get_cookies(response.headers.getlist('Set-Cookie'))
                    logger.debug(self.cookies)
                    request = request.replace(dont_filter=True)
                new_url = response.headers['Location'].decode('utf8')
                request = request.replace(url=new_url)
                request = request.replace(headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                    'Connection': 'keep-alive'})
                new_meta['headers_disable'] = True
                request = request.replace(meta=new_meta)
                logger.debug(request.url)
                logger.debug('response headers{}'.format(request.headers))
                return request
            except KeyError:
                return response
        else:
            try:
                logger.debug(response.headers['Location'])
            except KeyError:
                pass
            return response

    def get_cookies(self, raw):
        res = {}
        for one in raw:
            one = one.decode('utf8').split(';')[0]
            if 'cookie2' in one:
                tmp = one.split('=')[-1]
                if tmp:
                    res['cookie2'] = tmp
            elif '_tb_token_' in one:
                tmp = one.split('=')[-1]
                if tmp:
                    res['_tb_token_'] = tmp
            elif 't' in one:
                tmp = one.split('=')[-1]
                if tmp:
                    res['t'] = tmp
        return res
