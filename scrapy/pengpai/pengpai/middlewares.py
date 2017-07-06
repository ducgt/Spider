import logging as log
import requests
import subprocess
import time
from scrapy.utils.python import to_native_str


class CustomNormalMiddleware(object):
    def __init__(self):
        self.host = 'www.thepaper.cn'
        self.connection = 'keep-alive'
        self.accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3147.0 Safari/537.36'
        self.accept_encoding = 'gzip, deflate'
        self.accept_language = 'zh-CN,zh;q=0.8'
        self.Upgrade_Insecure_Requests = '1'
        self.cookies = {}
        self.request_count = 0
        # self.update_setting()

    def process_request(self, request, spider):
        self.request_count += 1
        if self.request_count > 1000:
            self.request_count = 0
            log.info('request more than 400,update setting')
            # self.update_setting()

        request.headers['User-Agent'] = self.user_agent
        request.headers['Accept'] = self.accept
        request.headers['Accept-Encoding'] = self.accept_encoding
        request.headers['Accept-Language'] = self.accept_language
        request.headers['Connection'] = self.connection
        request.headers['Host'] = self.host
        request.headers['Upgrade-Insecure-Requests'] = self.Upgrade_Insecure_Requests
        if self.cookies:
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
        cl = [to_native_str(c, errors='replace')
              for c in response.headers.getlist('Set-Cookie')]
        if cl:
            for one in cl:
                try:
                    tmp = one.split(';')[0]
                    k = tmp[:tmp.index('=')]
                    val = tmp[tmp.index('=')+1:]
                    self.cookies[k] = val
                except Exception as e:
                    log.warning(one, e)
            log.info(self.cookies)
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