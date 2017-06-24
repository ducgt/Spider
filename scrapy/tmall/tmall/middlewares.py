import logging as logger
from random import randint, uniform
import time
from selenium import webdriver
from selenium.webdriver import ActionChains


class CustomNormalMiddleware(object):
    def __init__(self):
        self.cookies = None
        path = "C:\Program Files (x86)\Google\Chrome\chromedriver.exe"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(service_args=['--load-images=no'], executable_path=path,
                                       chrome_options=chrome_options)
        self.action = ActionChains(self.driver)
        self.retry_login()

    def process_request(self, request, spider):
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36 TheWorld 7'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        request.headers['Accept-Encoding'] = 'gzip, deflate, sdch, br'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.8,zh-TW;q=0.6'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Host'] = 'www.tmall.com'
        # request.headers['cache-control'] = 'max-age=0'
        request.headers['upgrade-insecure-requests'] = 1
        request.headers['DNT'] = 1
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
        if response.status != 200:
            if response.status == 302 and response.headers['location']:
                logger.info('redirect to {}'.format(response.headers['location']))
                logger.info('response status 302,try relogin')
                time.sleep(randint(1, 5))
                self.retry_login()
                request = request.replace(dont_filter=True)
                return request
            else:
                logger.warning('response status not 200 {}'.format(response.status))
                return response
        else:
            return response

    def sendinfo(self):
        self.driver.find_element_by_id('TPL_username_1').clear()
        self.driver.find_element_by_id('TPL_username_1').send_keys('13902460164')
        time.sleep(1)
        self.driver.find_element_by_id('TPL_password_1').clear()
        self.driver.find_element_by_id('TPL_password_1').send_keys('poluo123')
        time.sleep(1)
        slipper = self.driver.find_element_by_css_selector('.nc_iconfont.btn_slide')
        if slipper:
            logger.info('get slipper')
            self.checkslipper()
        self.driver.find_element_by_id('J_SubmitStatic').click()

    def checkslipper(self):  # some problem
        slipper = self.driver.find_element_by_css_selector('.nc-lang-cnt')
        h_position = slipper.location
        logger.debug('-' * 30 + str(h_position))
        self.action.drag_and_drop_by_offset(slipper, h_position['x'] + 300, h_position['y']).perform()

    def retry_login(self):
        logger.info("Login Tmall")
        self.driver.get("https://login.tmall.com/")
        login_iframe = self.driver.find_element_by_id("J_loginIframe")
        if not login_iframe:
            logger.info('Not found tmall login iframe!')
            return
        self.driver.switch_to.frame(login_iframe)
        if self.driver.find_element_by_id('J_Quick2Static').is_displayed():
            self.driver.find_element_by_id('J_Quick2Static').click()
        time.sleep(0.5)

        self.sendinfo()
        time.sleep(uniform(1, 3))
        self.driver.get(
            'https://list.tmall.com/search_product.htm?spm=a221t.7059849.navcat0.7.x3sBGf&q=%C5%A3%BD%F2%D0%AC+%C4%D0&from=.list.pc_1_searchbutton&acm=lb-zebra-22355-807833.1003.4.764609&type=p&scm=1003.4.lb-zebra-22355-807833.OTHER_14732742070140_764609&smToken=3e88b50820f1498db3a8bf0d4a9d69d5&smSign=IaIp9mzjj1dUIPUPx64f7g%3D%3D')
        cookie = {}
        res = self.driver.get_cookies()
        for one in res:
            cookie[one['name']] = one['value']
        self.cookies = cookie
