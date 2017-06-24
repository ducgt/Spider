import requests
import re
import json

host = 'm.weibo.cn'
connection = 'keep-alive'
accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
accept_encoding='gzip, deflate, sdch, br'
accept_language ='zh-CN,zh;q=0.8,zh-TW;q=0.6'
x_requested_with = 'XMLHttpRequest'
dnt = '1'

custom_headers={'Host':host,'Connection':connection,'User-Agent':user_agent,'DNT':dnt,
'Accept':accept,'Accept-Encoding':accept_encoding,'Accept-Language':accept_language}
my_cookies = {}
verify_enable = True
count = 0

def get_cookies(data):
    data = data.split(';')
    tmp_dict = {}
    for one in data:
        if '_T_WM' in one:
            tmp_dict['_T_WM']= one[one.index('=')+1:]
        if 'M_WEIBOCN_PARAMS' in one:
            tmp_dict['M_WEIBOCN_PARAMS']= one.split('=')[-1]
    return tmp_dict

def process_start_url(start_url):
    global my_cookies
    r = requests.get(start_url,headers = custom_headers,verify=verify_enable)
    if r.status_code == 200:
        # print(r.text)
        my_cookies = get_cookies(r.headers['Set-Cookie'])
        
    else:
        print('url status code not 200!')
def process_profile_request(uid):
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=100505{}'.format(uid,uid)
    r = requests.get(url,headers = custom_headers,cookies = my_cookies,verify = verify_enable)
    if r.status_code!=200:
        print('status code = {}'.format(r.status_code))
    try:
        raw_data = json.loads(r.text)
        print('name {}'.format(raw_data['userInfo']['screen_name']))
    except Exception as e:
        print(e)
        print(r.text)

def process_activity_request(uid,page=1):
    global count
    if page== 1:
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}'.format(uid,uid)
    else:
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={}&containerid=107603{}&page={}'.format(uid,uid,page)
    print('activity page = {}'.format(page))
    r = requests.get(url,headers = custom_headers,cookies = my_cookies,verify = verify_enable)
    count += 1
    print('request_count = {}'.format(count))
    try:
        raw_data = json.loads(r.text)
    except Exception as e:
        print(e)
        print(r.text)
    if raw_data:
        return raw_data
    else:
        return None

def process_comment_request(a_id,page=1,next=False):
    global count
    max_page = page+1
    now_page = page
    while now_page <= max_page:
        url = 'https://m.weibo.cn/api/comments/show?id={}&page={}'.format(a_id,now_page)
        r = requests.get(url,headers = custom_headers,cookies = my_cookies,verify = verify_enable)
        count+=1
        print('request_count = {}'.format(count))
        if r.status_code != 200:
            return
        raw_data = json.loads(r.text)
        try:
            max_page = raw_data['max']
        except Exception as e:
            max_page = now_page
            return
        total_number = raw_data['total_number']
        print('max_page = {} total_number = {}'.format(max_page,total_number))
        print('now page = {}'.format(now_page))
        for one in raw_data['data']:
            print('user {} created_at {} text {}'.format(one['user']['screen_name'],one['created_at'],one['text']))
        now_page += 1

if __name__ == '__main__':
    uid = 1195242865
    start_url = 'https://m.weibo.cn/p/100505{}'.format(uid)
    process_start_url(start_url)
    print(my_cookies)
    if my_cookies:
        process_profile_request(uid)
        page = 6
        while True:
            act = process_activity_request(uid,page)
            if act:
                for one in act['cards']:
                    a_id = one['mblog']['id']
                    print('text {} a_id {}'.format(one['mblog']['text'],a_id))
                    process_comment_request(a_id,next=True)
                try:
                    page  = act['cardlistInfo']['page']
                except Exception as e:
                    print(e)
                    break
            else:
                break
            


