import js2py
import requests
import time
import re
from bs4 import BeautifulSoup
from lxml import html

code = 't = (new Date).getTime(),\
            "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(e) {\
                var r, n;\
                return r = (t + 16 * Math.random()) % 16 | 0,\
                t = Math.floor(t / 16),\
                n = "x" === e ? r : 3 & r | 8,\
                n.toString(16)\
            })'

# js2py.eval_js(code)
session = requests.session()
start_url =  'https://www.itjuzi.com/investevents'
def update_cookie(cookies,dic):
    requests.utils.add_dict_to_cookiejar(cookies,dic)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
    }

r = session.get(start_url,headers = headers,verify=False)

tree = html.fromstring(r.text)
account_id_text = tree.xpath('/html/body/script[8]/text()')
try:
    tmp = re.findall(r'\'\w{32}\'',account_id_text[0])[0]
except Exception as e:
    print('account id error')
    tmp = None
print(tmp)
gr_session_id_key = 'gr_session_id_'+tmp.replace('\'','')
gr_session_id_value = js2py.eval_js(code)
gr_user_id = js2py.eval_js(code)
lvpt = str(int(time.time()*1000))
my_cookie = {'Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89':time.time(),'_gid':'GA1.2.1719831259.'+lvpt,
    '_ga':'GA1.2.254136326.'+lvpt,'Hm_lvt_1c587ad486cdb6b962e94fc2002edf89':'1499431470,1499431575,1499431677,'+lvpt,
    'Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89':lvpt,gr_session_id_key:gr_session_id_value,'gr_user_id':gr_user_id
}
update_cookie(session.cookies,my_cookie)

r = session.get('https://www.itjuzi.com/investevents',headers = headers,verify=False)
print(r.status_code)
post_url = 'https://www.itjuzi.com/user/login?redirect=investevents&flag='
play_data = {
    'identity':user,
    'password':password,
    'remember':'1',
    'page':'',
    'url':''
}
r = session.post(post_url,headers=headers,data=play_data,verify=False)
print(r.status_code)
print(r.headers)

r = session.get('http://radar.itjuzi.com/company/58796',headers=headers,verify=False)
print(r.status_code)
if r.status_code==200:
    print(r.text)

