# _*_  coding:utf-8_*_
"""
妹子爬虫 xpath 解析网址  2018.11.28
"""
__author__ = "open_china"

import os
import time
from threading import Thread

import numpy as np
import requests
from lxml import html
from requests.cookies import RequestsCookieJar


def dev_list(lis, n):
    size = int(len(lis) / n)
    res_list = np.array(lis[:size * n]).reshape(size, n).tolist()
    if size * n < len(lis):
        res_list.append(lis[size * n:])
    return res_list


class Spider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Referer': "http://www.mzitu.com/"
        }
        self.baseUrl = "https://www.mzitu.com"
        self.cookie_jar = RequestsCookieJar()
        self.cookie_jar.set("MZITU", "B1CCDD4B4BC886BF99364C72C8AE1C01:FG=1", domain="mzitu.com")

    def get_page(self):
        print(self.baseUrl)
        print(requests.get(self.baseUrl, headers=self.headers))
        selector = html.fromstring(requests.get(self.baseUrl, headers=self.headers).content)
        urls = []
        for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
            urls.append(i)
        print(urls)
        return urls

    def get_pic_link(self, url):
        print("we visit:" + url)
        try:
            sel = html.fromstring(requests.get(url, headers=self.headers).content)
        except Exception as e:
            print(e)
            return
        total = sel.xpath('//div[@class="pagenavi"]/a/span/text()')[-2]
        title = sel.xpath('//h2[@class="main-title"]/text()')[0]
        print(title + "  " + "总共: " + str(total) + "张")
        jpg_list = []
        print("total:", total)
        for i in range(int(total)):
            link = "{}/{}".format(url, i + 1)
            print(link)
            s = html.fromstring(requests.get(link, headers=self.headers).content)
            if len(s.xpath('//div[@class="main-image"]/p/a/img/@src')) > 0:
                jpg_list.append(s.xpath('//div[@class="main-image"]/p/a/img/@src')[0])
            else:
                print("pass-----")
        return title, jpg_list

    def get_pic(self, title, pic_list):
        count = len(pic_list)
        dir_name = u"【%sP】%s" % (str(count), title)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        k = 1
        down_list = dev_list(pic_list, 60)  # 切换为10个下载一次
        for per in down_list:
            threads = []
            for url in per:  # 开启多线程下载
                filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dir_name, k)
                k = k + 1
                t = Thread(target=self.download, args=[filename, url])
                t.start()
                threads.append(t)
            for t in threads:  # 开启守护进程
                t.join()

    def download(self, filename, url):
        if os.path.exists(filename):
            return
        with open(filename, "wb") as jpg:
            try:
                jpg.write(requests.get(url, headers=self.headers, timeout=60).content)
                print("下载成功:" + filename)
                time.sleep(0.1)
            except Exception as e:
                print(e)

    def start(self):
        urls = self.get_page()
        for item in urls:
            title, pic_list = self.get_pic_link(item)
            self.get_pic(title, pic_list)
            # break


if __name__ == "__main__":
    Spider().start()
