import logging as logger
import furl
import random
import subprocess
import time


class MyCustomDownloaderMiddleware(object):
    def __init__(self):
        self.request_count = 0
        self.cookies = None
        # self.change_ip()

    def process_request(self, request, spider):
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        request.headers['Accept-Encoding'] = 'gzip, deflate'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
        request.headers['Connection'] = 'keep-alive'
        # request.headers['Referer'] = 'http://www.jyeoo.com/math/ques/search'
        request.headers['Upgrade-Insecure-Requests'] = '1'
        request.headers['Host'] = 'www.jyeoo.com'
        if request.meta.get('cookie'):
            logger.debug('cookie enable')
            parms = request.meta.get('parms')
            key_word = request.meta.get('word')
            request.cookies = self.get_cookies(parms, key_word)
        self.request_count += 1
        if self.request_count > 15000:
            logger.info('count more than 15000,need change ip')
            self.change_ip()

    def get_cookies(self, parms, key_word):
        res = {}
        for k, v in parms.items():
            if k == 'q':
                res['j_{}_q_q_1'.format(key_word)] = str(v)
            if k == 'f':
                res['j_{}_q_f'.format(key_word)] = str(v)
            if k == 'ct':
                res['j_{}_q_ct'.format(key_word)] = str(v)
            if k == 'dg':
                res['j_{}_q_dg'.format(key_word)] = str(v)
            if k == 'fg':
                res['j_{}_q_fg'.format(key_word)] = str(v)
            if k == 'pd':
                res['j_{}_q_pd'.format(key_word)] = str(v)
            if k == 'po':
                res['j_{}_q_po'.format(key_word)] = str(v)
            if k == 'so':
                res['j_{}_q_so'.format(key_word)] = str(v)
            if k == 'so2':
                res['j_chemistry_q_f'] = str(v)
            res['j_chemistry_q_f'] = str(1)
            res['j_chinese_q_f'] = str(1)
            res['j_physics_q_f'] = str(1)
            res['j_politics_q_f'] = str(1)
            res['q_lbs'] = ''
            res['JYERN'] = str(random.uniform(0, 1))
            res['JYERN'] = str(random.uniform(0, 1))
            res['CNZZDATA2018550'] = 'cnzz_eid%3D875842140-1499776927-%26ntime%3D1499778015'
            res['UM_distinctid'] = '15d2c7da24640-0a061e52eb4413-8383667-1fa400-15d2c7da247190'
        logger.debug('cookies {}'.format(res))
        return res

    def process_response(self, request, response, spider):
        if response.status != 200:
            if self.request_count < 5:
                return request
            logger.info('response status not 200,need change ip {}'.format(response.status))
            self.change_ip()
            return request
        else:
            return response

    def change_ip(self):
        self.request_count = 0
        # status, res = subprocess.getstatusoutput('adsl-stop')
        # if status == 0:
        #     logger.debug('adsl stop success')
        # else:
        #     logger.warning('adsl stop failed')
        # time.sleep(0.5)
        # status, res = subprocess.getstatusoutput('adsl-start')
        # if status == 0:
        #     logger.debug('adsl start success')
        # else:
        #     logger.warning('adsl start failed')
