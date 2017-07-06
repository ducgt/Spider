# -*- coding: utf-8 -*-
import time
import subprocess
import pymongo
import os
import shutil
import json

mongo_uri='mongodb://poluo:poluo123@localhost:27017/data'
client = pymongo.MongoClient(mongo_uri)
db = client['data']
col = db.monitor

def insert_value(value):
    data ={'data':value,'time':int(time.time())}
    col.insert(data)

def make_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    if not os.path.exists(dir):
        os.makedirs(dir)

def crawl():
    count = 0
    make_dir('./log')
    while True:
        count+=1
        status, res = subprocess.getstatusoutput('scrapy crawl news')
        if status == 0:
            print(res)
        else:
            print('crawl failed {}'.format(res))
        for file in os.listdir(os.getcwd()):
            if  os.path.isfile(file) and 'res_' in file:
                with open(file,'r') as fobj:
                    try:
                        res = json.load(fobj)
                    except Exception as e:
                        print(e)
                        res = None
                    if res:
                        shutil.copy(file,'./log/{}'.format(file))
                        insert_value(res)
                        print(res)
                os.remove(file)
        print('loop {} finished'.format(count))
        time.sleep(60*30)

if __name__ == '__main__':
    crawl()
