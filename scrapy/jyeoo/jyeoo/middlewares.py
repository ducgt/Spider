import logging as logger
import random
import subprocess
import time


class MyCustomDownloaderMiddleware(object):
    def __init__(self):
        self.request_count = 0
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
        self.request_count += 1
        if self.request_count > 15000:
            logger.info('count more than 15000,need change ip')
            self.change_ip()

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
