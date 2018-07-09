import requests
from bs4 import BeautifulSoup

from http import client

import urllib
from threading import Thread
from threading import Lock

url = 'http://www.xicidaili.com/nn/%d'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
}

inFile = open('./proxy.txt',mode='r',encoding='utf-8')
outFile = open('./verifiedProxy.txt',mode='w',encoding='utf-8')
lock = Lock()

def getProxy(page):
    fp = open('./proxy.txt',mode='a',encoding='utf-8')
    num = 0
    for p in range(1,page+1):
        url_proxy = url%(p)
        response = requests.get(url = url_proxy,headers=headers)
        response.encoding = 'utf-8'
        html = response.text

        soup = BeautifulSoup(html)
        proxies = soup.find('table',id='ip_list').find_all('tr')
        # print(len(proxies))

        for p in proxies[1:]:
            tds = p.find_all('td')
            ip =tds[1].string
            port = tds[2].string
            #ip位置有可能为空
            try:
                address = tds[3].find('a').string
            except:
                address = '未知'
            protocal = tds[5].string
            speed = tds[6].div['title']
            stay = tds[8].get_text()
            last_verified_time = tds[9].get_text()

            proxy = '%s,%s,%s,%s,%s,%s,%s\n'%(ip,port,address,protocal,speed,stay,last_verified_time)
            fp.write(proxy)
            num+=1
    fp.close()
    return num


def verifyProxy():
    verify_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    }
    verify_url = 'http://www.baidu.com/'
    check_num = 0
    while True:
        lock.acquire()
        line = inFile.readline().strip()
        lock.release()

        if line == None:break
        try:
            list_line = line.split(',')
            ip = list_line[0]
            port = list_line[1]
        except Exception as e:
            break

        #方式一
        # requests.get(verify_url,proxies = {'http':'%s:%s'%(ip,port)})
        #方式二
        # handler = urllib.request.ProxyHandler({'http': '%s:%s' % (ip, port)})
        # opener = urllib.request.build_opener(handler)

        #方式三：
        conn = client.HTTPConnection(ip,port,timeout=5)
        try:
            conn.request('GET',verify_url,headers = verify_headers)
            #如果不报异常，说明ip和端口号可用
            print('+++Success+++%s'%line)
            lock.acquire()
            outFile.write(line+'\n')
            lock.release()
            check_num += 1
        except:
            print('-----Failure----%s'%(line))
    return check_num



if __name__ == '__main__':
    # page = int(input('请输入爬取的页码：'))
    # num =getProxy(page)
    # print('国内高级代理获取了：%d'%num)

    print('开始验证代理ip-----')
    # inFile = open('./proxy.txt',mode='r',encoding='utf-8')
    # outFile = open('./verifiedProxy.txt',mode='a',encoding='utf-8')
    # check_num = verifyProxy(inFile,outFile)
    # print('可用的ip数量是：%d'%(check_num))

    threads = []

    for i in range(30):
        th = Thread(target=verifyProxy)
        th.start()
        threads.append(th)

    #线程锁
    for th in threads:
        th.join()

    #关闭文件流
    inFile.close()
    outFile.close()