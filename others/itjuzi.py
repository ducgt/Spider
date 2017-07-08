import js2py
import requests
import time
import re
from bs4 import BeautifulSoup
from lxml import html


class Spider_itjuzi(object):
    """docstring for Spider_itjuzi"""
    def __init__(self, debug = False):
        super(Spider_itjuzi, self).__init__()
        if debug == True:
            self.verify_parm = False
        else:
            self.verify_parm = True
        self.session_id = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3151.4 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
            }
        # first step get cookie from server
        self.session = requests.Session()
        init_url =  'https://www.itjuzi.com/investevents'
        r = self.session.get(init_url,headers = self.headers,verify=self.verify_parm)
        # second step,calcuate cookies
        my_cookie = self.calculate_cookies(r.text)
        # third step,update session cookies
        self.update_cookie(my_cookie)
        # login
        if self.login():
            print('init ok')
        else:
            print('init failed')
        self.rader_falg = False
        

    def calculate_cookies(self,text):
        tree = html.fromstring(text)
        account_id_text = tree.xpath('/html/body/script[8]/text()')
        try:
            tmp = re.findall(r'\'\w{32}\'',account_id_text[0])[0]
        except Exception as e:
            print('account id error')
            return None

        gr_session_id_key = 'gr_session_id_'+tmp.replace('\'','')
        gr_session_id_value = self.excute_js()
        self.session_id = gr_session_id_key
        gr_user_id = self.excute_js()
        lvpt = str(int(time.time()*1000))
        my_cookie = {'Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89':time.time(),'_gid':'GA1.2.1719831259.'+lvpt,
            '_ga':'GA1.2.254136326.'+lvpt,'Hm_lvt_1c587ad486cdb6b962e94fc2002edf89':'1499431470,1499431575,1499431677,'+lvpt,
            'Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89':lvpt,gr_session_id_key:gr_session_id_value,'gr_user_id':gr_user_id
        }
        return my_cookie

    def calculate_cookies2(self,text):
        tree = html.fromstring(text)
        try:
            tmp = re.findall(r'\'\w{16}\'',text)[0]
        except Exception as e:
            print('account id error')
            return None
        pgv_pvi = self.excute_js2()
        pgv_si = 's'+self.excute_js2()
        gr_session_id_key = 'gr_session_id_'+tmp.replace('\'','')
        gr_session_id_value = self.excute_js()
        my_cookie = {gr_session_id_key:gr_session_id_value,'pgv_pvi':pgv_pvi,'pgv_si':pgv_si}
        return my_cookie

    @staticmethod
    def excute_js():
        code = 't = (new Date).getTime(),\
                "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(e) {\
                    var r, n;\
                    return r = (t + 16 * Math.random()) % 16 | 0,\
                    t = Math.floor(t / 16),\
                    n = "x" === e ? r : 3 & r | 8,\
                    n.toString(16)\
                })'
        res = js2py.eval_js(code)
        return res
    @staticmethod
    def excute_js2():
        code='function r(c) {\
        return (c || "") + Math.round(2147483647 * (Math.random() || .5)) * +new Date % 1E10\
        }\
        r()'
        res = js2py.eval_js(code)
        return res

    def update_cookie(self,dic,delete=False):
        requests.utils.add_dict_to_cookiejar(self.session.cookies,dic)
        if delete:
            tmp = requests.utils.dict_from_cookiejar(self.session.cookies)
            del tmp[self.session_id]
            tmp['_gat'] = '1'
            self.session.cookies.clear()
            requests.utils.add_dict_to_cookiejar(self.session.cookies,tmp)

    def login(self):
        print('login first step,verify cookie')
        r = self.session.get('https://www.itjuzi.com/investevents',headers = self.headers,verify=self.verify_parm)
        if r.status_code == 200:
            print('login verify cookie ok')
        else:
            print('login verify cookie failed')
            return None

        post_url = 'https://www.itjuzi.com/user/login?redirect=investevents&flag='
        play_data = {
            'identity':'997786818@qq.com',
            'password':'poluo123',
            'remember':'1',
            'page':'',
            'url':''
        }
        print('login second step,post data')
        r = self.session.post(post_url,headers=self.headers,data=play_data,verify=self.verify_parm)
        if r.status_code == 200:
            print('login post data ok')
        else:
            print('login post data failed {}'.fromat(r.status_code))
            return None
        print('login third verify login valid')
        r = self.session.get('http://radar.itjuzi.com/company/58796',headers=self.headers,verify=self.verify_parm)
        if r.status_code==200:
            print('login verify login ok')
        else:
            print('login verify login failed {}'.fromat(r.status_code))
            return None
        return True

    def get_invest_events(self):
        res = []
        url = 'https://www.itjuzi.com/investevents'
        while True:
            r = self.session.get(url,headers=self.headers,verify=self.verify_parm)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text,'lxml')
                event_list = soup.select('div.list-main-eventset-finan > ul:nth-of-type(2) > li')
                for one in event_list:
                    date = one.select('i.cell.date > span')[0].text
                    name = one.select('i.cell.maincell > p.title')
                    round_tag = one.select('i.cell.round > a > span')[0].text
                    money = one.select('i.cell.money')[0].text
                    investorset = one.select('i.cell.name > div.investorset')
                    url = one.select('i.cell.pic > a')[0]['href']
                    company_id = url.split('/')[-1]
                    print('{} {}　{} {} {} {}'.format(date,name,round_tag,money,investorset,url))
                    res.append(company_id)
            else:
                print('status code not right {}'.format(self.status_code))
            url_list = soup.select('div.ui-pagechange.for-sec-bottom > a')
            for one in url_list[::-1]:
                if one.text == '下一页 →':
                    next_url = one['href']
                    break
            if next_url:
                url = next_url
                time.sleep(0.5)
                print('next page {}'.format(url))
                break
            else:
                print('no next page')
                break
        print('get {} company id'.format(len(res)))
        return res
    def parse_radar(self,url):
        if not self.rader_falg:
            company_id = url.split('/')[-1]
            tmp_url = 'http://radar.itjuzi.com/company/' + company_id
            r = self.session.get(tmp_url,headers=self.headers)
            my_cookie = self.calculate_cookies2(r.text)
            self.update_cookie(my_cookie,delete = True)
            self.rader_falg = True
            self.headers['Origin'] = 'http://radar.itjuzi.com'
            self.headers['Referer'] = 'http://radar.itjuzi.com/company/58796'
            self.headers['X-Requested-With'] = 'XMLHttpRequest'
        r = self.session.post(url,headers=self.headers)
        print(r.text)

if __name__ == '__main__':
    my_spider = Spider_itjuzi(True)
    comany_id_list = my_spider.get_invest_events()
    for one in comany_id_list:
        url = 'http://radar.itjuzi.com/company/getinvchartdata/'+one
        my_spider.parse_radar(url)