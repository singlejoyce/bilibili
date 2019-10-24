# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2019/04/16--17:12
import hashlib
import random
from datetime import datetime
import os
import sys
import re
from moviepy.editor import *
import asyncio
import aiohttp
import requests
import time
import urllib.request
from tqdm import tqdm

__author__ = 'Joyce'


class Logger(object):
    def __init__(self, file="log.txt"):
        self.terminal = sys.stdout
        self.log = open(file, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 "
    "Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 "
    "Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 "
    "Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

# 免费代理IP不能保证永久有效，如果不能用可以更新
# http://www.goubanjia.com/
proxy_list = [
    '113.195.153.156:9999',
    '222.175.171.6:8080',
    '103.10.86.203:8080',
    '117.28.97.143:9999',
    '59.57.149.115:9999',
    '27.152.91.71:9999',
    '121.15.254.156:888',
    '117.30.112.17:9999',
    '117.30.112.185:9999',
    '59.57.38.126:9999',
    '222.89.32.160:9999',
    '59.37.18.243:3128',
    '117.30.113.69:9999',
    '42.228.3.158:8080',
    '27.152.91.71:9999',
    '183.164.238.18:9999',
]
proxies = {"http": "http://" + random.choice(proxy_list),
           'https': "https://" + random.choice(proxy_list)
           }


def format_size(filesize):
    if filesize < 1000:
        return '%i' % filesize + 'size'
    elif 1000 <= filesize < 1000000:
        return '%.1f' % float(filesize / 1000) + 'KB'
    elif 1000000 <= filesize < 1000000000:
        return '%.1f' % float(filesize / 1000000) + 'MB'
    elif 1000000000 <= filesize < 1000000000000:
        return '%.1f' % float(filesize / 1000000000) + 'GB'
    elif 1000000000000 <= filesize:
        return '%.1f' % float(filesize / 1000000000000) + 'TB'


def get_video_url(cid, url, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
        'Referer': url,  # 注意加上referer
        'User-Agent': random.choice(my_headers),
    }
    res = requests.get(url_api, headers=headers).json()
    video_list = []
    video_size_list = []
    for i in res['durl']:
        video_list.append(i['url'])
        video_size_list.append(i['size'])
    return video_list, video_size_list


def download_from_url(down_url, file, ref_url):
    headers = {'host': down_url.split('/')[2],
               'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.5',
               'Origin': 'https://www.bilibili.com',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive',
               'Referer': ref_url,
               'User-Agent': random.choice(my_headers),
               'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;'}
    # print('[%s 开始下载视频......]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    try:
        response = requests.get(down_url, headers=headers, stream=True, verify=False)
        file_size = int(response.headers['content-length'])
        if os.path.exists(file):
            first_byte = os.path.getsize(file)
        else:
            first_byte = 0
        if first_byte >= file_size:
            return file_size
        headers['Range'] = f"bytes={first_byte}-{file_size}"
        pbar = tqdm(total=file_size, initial=first_byte, unit='B',
                    unit_scale=True, desc=file)
        time.sleep(0.5)
        req = requests.get(down_url, headers=headers, stream=True, verify=False)
        with (open(file, 'ab')) as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(1024)
        pbar.close()
    except Exception as e:
        print("%s 下载异常:%s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))
    # else:
    #     print('[%s 视频下载完成!]' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


async def fetch(session, down_url, dst, pbar=None, headers=None):
    if pbar:
        async with session.get(down_url, headers=headers) as req:
            with(open(dst, 'ab')) as f:
                while True:
                    chunk = await req.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(1024)
            pbar.close()
            # print('[%s 视频下载完成!]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    else:
        async with session.get(down_url, headers=headers) as req:
            return req


async def async_download_from_url(down_url, file, ref_url):
    """异步"""
    headers = {'host': down_url.split('/')[2],
               'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.5',
               'Origin': 'https://www.bilibili.com',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive',
               'Referer': ref_url,
               'Range': 'bytes=0-',
               'User-Agent': random.choice(my_headers),
               'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;'}
    # print('[%s 开始下载视频......]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    async with aiohttp.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            req = await fetch(session, down_url, file, headers=headers)
            file_size = int(req.headers['content-length'])
            if os.path.exists(file):
                first_byte = os.path.getsize(file)
            else:
                first_byte = 0
            if first_byte >= file_size:
                return file_size
            headers['Range'] = f"bytes={first_byte}-{file_size}"
            pbar = tqdm(total=file_size, initial=first_byte, unit='B',
                        unit_scale=True, desc=file)
            await fetch(session, down_url, file, pbar=pbar, headers=headers)


# 合并视频
def combine_video(file_list, outpath):
    # 定义一个数组
    L = []
    for file in file_list:
        # 载入视频
        video = VideoFileClip(file)
        # 添加到数组
        L.append(video)
    # 拼接视频
    final_clip = concatenate_videoclips(L)
    # 生成目标视频文件
    final_clip.to_videofile(outpath, fps=24, remove_temp=False)


def do_prepare(inputstart):
    print('[%s start!]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if inputstart.isdigit():
        # 如果输入的是av号
        # 获取cid的api, 传入aid即可
        aid = inputstart
    else:
        # 如果输入的是url (eg: https://www.bilibili.com/video/av46958874/)
        aid = re.search(r'/av(\d+)/*', inputstart).group(1)

    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + aid
    # qn参数就是视频清晰度 可选值：
    # 116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频)
    # 112: 高清1080P+ (hdflv2)(需要大会员)
    # 80: 高清1080P (flv)
    # 74: 高清720P60 (需要大会员)
    # 64: 高清720P (flv720)
    # 32: 清晰480P (flv480)
    # 16: 流畅360P (flv360)
    qn = 80
    # 随机选择一个Header伪装成浏览器
    headers = {'User-Agent': random.choice(my_headers)}
    # 获取视频的cid,title
    time.sleep(0.5)
    html = requests.get(start_url, headers=headers).json()
    data = html['data']
    aid_title = re.sub(r'[/\\:*?"<>|]', '', data['title'].replace(' ', ''))  # 替换为空的
    # 创建文件夹,存放下载的视频和日志文件
    down_video_path = os.path.join("d:\\", 'bilibili_video', aid_title)  # 当前目录作为下载目录
    if not os.path.exists(down_video_path):
        os.makedirs(down_video_path)
    sys.stdout = Logger(os.path.join(down_video_path, "log.txt"))
    cid_list = []
    if '?p=' in inputstart:
        # 单独下载分P视频中的一集
        p = re.search(r'\?p=(\d+)', inputstart).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        # 如果p不存在就是全集下载
        cid_list = data['pages']
    tasks = []

    for item in cid_list:
        cid = str(item['cid'])
        # 处理视频名称
        title = item['part']
        title = re.sub(r'[/\\:*?"<>|]', '', title.replace(' ', ''))  # 替换为空的
        # 秒数转成时分秒
        m, s = divmod(item['duration'], 60)
        h, m = divmod(m, 60)
        duration = '{}:{}:{}'.format(h, m, s)
        # 获得视频的大小以及下载地址
        page_url = start_url + "/?p=" + str(item['page'])
        video_list = get_video_url(cid, page_url, qn)
        total_size = 0
        for i in video_list[1]:
            total_size += i
            down_url_list = video_list[0]
        print('[视频的title]:{}\n[视频的cid]:{}  [视频的总size]:{}  [视频的duration]:{}'.format(title, cid, format_size(total_size), duration))
        print('[视频的downurl]:{}'.format(down_url_list))

        # 单线程单个下载（支持断点续传）
        if len(down_url_list) > 1:
            file_list = []
            for i in range(len(down_url_list)):
                filename = os.path.join(down_video_path, r'{}-{}.flv'.format(title, i+1))
                file_list.append(filename)
                # 下载方式:单线程下载（支持断点续传）
                download_from_url(down_url_list[i], filename, page_url)
                # 下载方式:单线程+异步协程下载（支持断点续传）
                # task = asyncio.ensure_future(async_download_from_url(down_url_list[i], filename, page_url))
                # tasks.append(task)
            # 最后合并视频(合并效率太慢，暂不使用了)
            # filename = os.path.join(down_video_path, r'{}.mp4'.format(title))
            # combine_video(file_list, filename)
        else:
            filename = os.path.join(down_video_path, r'{}.flv'.format(title))
            download_from_url(down_url_list[0], filename, page_url)
            # 下载方式:asyncio和aiohttp模块异步协程下载（支持断点续传）
            # task = asyncio.ensure_future(async_download_from_url(down_url_list[0], filename, page_url))
            # tasks.append(task)

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.wait(tasks))
    # loop.close()

    print('[%s end！]' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    # 如果是windows系统，下载完成后打开下载目录
    if sys.platform.startswith('win'):
        os.startfile(down_video_path)


if __name__ == '__main__':
    # 用户输入av号或者视频链接地址
    print('*' * 30 + 'B站视频下载小助手' + '*' * 30)
    # start = input('请输入您要下载的B站av号或者视频链接地址:')
    do_prepare('56029711')


# 分P视频下载测试: https://www.bilibili.com/video/av19516333/
# 需要合并的视频： https://www.bilibili.com/video/av12084723/

