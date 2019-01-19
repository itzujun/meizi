
### 妹子爬虫

-爬虫多进程
```
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
```
### 爬虫结果
![](https://github.com/itzujun/meizi/blob/master/bmp/result.jpg)



