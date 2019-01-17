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


class Spider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Referer': "http://www.mzitu.com/"
        }
        self.baseUrl = "http://www.mzitu.com/"
        self.session = requests.Session()
        self.cookie_jar = RequestsCookieJar()
        self.cookie_jar.set("MZITU", "B1CCDD4B4BC886BF99364C72C8AE1C01:FG=1", domain="mzitu.com")

    def getPage(self):
        selector = html.fromstring(self.session.get(self.baseUrl).content)
        urls = []
        for i in selector.xpath('//ul[@id="pins"]/li/a/@href'):
            urls.append(i)
        return urls

    def getPicclink(self, url):
        print("we visit:" + url)
        try:
            sel = html.fromstring(self.session.get(url, cookies=self.cookie_jar).content)
        except Exception as e:
            print(e)
            return
        total = sel.xpath('//div[@class="pagenavi"]/a/span/text()')[-2]
        title = sel.xpath('//h2[@class="main-title"]/text()')[0]
        print(title + "  " + "总共: " + str(total) + "张")
        jpglist = []
        for i in range(int(total)):
            link = "{}/{}".format(url, i + 1)
            s = html.fromstring(self.session.get(link, cookies=self.cookie_jar).content)
            jpglist.append(s.xpath('//div[@class="main-image"]/p/a/img/@src')[0])
        return title, jpglist

    def getPic(self, title, piclist):
        count = len(piclist)
        dirName = u"【%sP】%s" % (str(count), title)
        if not os.path.exists(dirName):
            os.makedirs(dirName)
        k = 1
        downlist = self.devlist(piclist, 60)  # 切换为10个下载一次
        for per in downlist:
            threads = []
            for url in per:  # 开启多线程下载
                filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirName, k)
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
                jpg.write(self.session.get(url, headers=self.headers, timeout=60, cookies=self.cookie_jar).content)
                print("下载成功:" + filename)
                time.sleep(0.1)
            except Exception as e:
                print(e)

    def devlist(self, lis, n):
        size = int(len(lis) / n)
        reslis = np.array(lis[:size * n]).reshape(size, n).tolist()
        if size * n < len(lis):
            reslis.append(lis[size * n:])
        return reslis

    def start(self):
        urls = self.getPage()
        for item in urls:
            title, piclist = self.getPicclink(item)
            self.getPic(title, piclist)
            # break


if __name__ == "__main__":
    Spider().start()
