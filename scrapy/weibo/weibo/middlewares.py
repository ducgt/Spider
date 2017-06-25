import logging as log
import requests
import json
import subprocess
import time


class CustomNormalMiddleware(object):
    def __init__(self):
        self.host = 'm.weibo.cn'
        self.connection = 'keep-alive'
        self.accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        self.accept_encoding = 'gzip, deflate, sdch, br'
        self.accept_language = 'zh-CN,zh;q=0.8,zh-TW;q=0.6'
        self.x_requested_with = 'XMLHttpRequest'
        self.dnt = '1'
        self.cookies = None
        self.request_count = 0
        self.update_setting()

    def process_request(self, request, spider):
        self.request_count += 1
        if self.request_count > 1000:
            self.request_count = 0
            log.info('request more than 400,update setting')
            self.update_setting()

        request.headers['User-Agent'] = self.user_agent
        request.headers['Accept'] = self.accept
        request.headers['Accept-Encoding'] = self.accept_encoding
        request.headers['Accept-Language'] = self.accept_language
        request.headers['Connection'] = self.connection
        request.headers['Host'] = self.host
        request.headers['DNT'] = self.dnt
        request.headers['X-Requested-With'] = self.x_requested_with
        request.cookies = self.cookies

    def update_setting(self):
        while True:
            self.request_count = 0
            self.change_proxy()
            self.get_new_cookie()
            if self.cookies != {}:
                log.info('get cookie {}'.format(self.cookies))
                break
            else:
                log.info('cookies in empty,try again')

    def process_response(self, request, response, spider):
        if '出错了403' in response.text or response.status != 200:
            log.info('微博-出错了403')
            self.update_setting()
            request = request.replace(dont_filter=True)
            return request
        else:
            return response

    @staticmethod
    def change_proxy():
        status, res = subprocess.getstatusoutput('adsl-stop')
        if status == 0:
            log.debug('adsl stop success')
        else:
            log.warning('adsl stop failed')
        time.sleep(0.5)
        status, res = subprocess.getstatusoutput('adsl-start')
        if status == 0:
            log.debug('adsl start success')
        else:
            log.warning('adsl start failed')

    def get_new_cookie(self):
        uid = 1195242865
        start_url = 'https://m.weibo.cn/p/100505{}'.format(uid)
        custom_headers = {'Host': self.host,
                          'Connection': self.connection,
                          'User-Agent': self.user_agent,
                          'DNT': self.dnt,
                          'Accept': self.accept,
                          'Accept-Encoding': self.accept_encoding,
                          'Accept-Language': self.accept_language}
        r = requests.get(start_url, headers=custom_headers, verify=False)
        if r.status_code == 200:
            data = r.headers['Set-Cookie']
            data = data.split(';')
            tmp_dict = {}
            for one in data:
                if '_T_WM' in one:
                    tmp_dict['_T_WM'] = one[one.index('=') + 1:]
                if 'M_WEIBOCN_PARAMS' in one:
                    tmp_dict['M_WEIBOCN_PARAMS'] = one.split('=')[-1]
            if tmp_dict:
                self.cookies = tmp_dict
