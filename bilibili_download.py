# !/usr/bin/python3
# -*- coding:utf-8 -*-

import hashlib
import random
from datetime import datetime
import os
import sys
import re
import subprocess
from moviepy.editor import *
import asyncio
import aiohttp
import requests
import time
import urllib.request
from tqdm import tqdm

from logger import Logger

__author__ = 'Joyce'

# ffmpeg路径配置
ffmpeg = 'D:/ffmpeg-20191022-0b8956b-win64-static/bin/ffmpeg'


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
    mylogger.info('[get_video_url] url_api={}'.format(url_api))
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
        mylogger.error("[download_from_url] 下载异常:%s" % e)


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
def concat_video(file_list, video_path, pname_list):
    mylogger.info('[concat_video] start...')
    for i in range(len(file_list)):
        current_video_path = os.path.join(video_path, file_list[i])
        mylogger.info('[concat_video] 视频{}合并中...'.format(file_list[i]))
        # ！！！路径是反斜杠ffmepg合并时会报错 returned non-zero exit status 1.
        temp_file_path = os.path.join(current_video_path, 'filelist.txt').replace('\\', '/')
        merge_file_path = os.path.join(current_video_path, r'{}.mp4'.format(pname_list[i])).replace('\\', '/')
        try:
            with open(temp_file_path, 'w') as f:
                for file_name in os.listdir(current_video_path):
                    if file_name.endswith('.flv'):
                        f.write("file  '" + file_name + "'\n")
            # 使用ffmpeg进行多个视频合并过程中出现了“unsafe file name”错误，解决的办法是加个-safe 0 参数
            cmd = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c', 'copy', merge_file_path]
            proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception as e:
            raise Exception()
    mylogger.info('[concat_video] end!')


def start_download(down_list, down_path):
    mylogger.info('[start_download] start......')
    for result in down_list:
        down_url_list = result['down_url_list']
        page = result['page']
        title = result['pname']
        purl = result['purl']
        # 单线程单个下载（支持断点续传）
        if len(down_url_list) > 1:
            # 如果分P视频是多段视频，视频下载目录以单P的文件夹方式存放
            down_p_video_path = os.path.join(down_path, page)
            if not os.path.exists(down_p_video_path):
                os.makedirs(down_p_video_path)
            for i in range(len(down_url_list)):
                file_dir = os.path.join(down_p_video_path, r'{}_{:0>3}.flv'.format(title, i))
                download_from_url(down_url_list[i], file_dir, purl)
        else:
            # 如果分P视频是单个视频，视频下载目录直接存放在下载目录
            download_from_url(down_url_list[0], os.path.join(down_path, r'{}.flv'.format(title)), purl)

    mylogger.info('[start_download] end!')


def do_prepare(inputstart, inputqn, aid):
    mylogger.info('[do_prepare] start......')
    result_list = []
    # 开始获取视频信息
    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + aid
    mylogger.info('[do_prepare] start_url={}'.format(start_url))
    qn = inputqn
    # 随机选择一个Header伪装成浏览器
    headers = {'User-Agent': random.choice(my_headers)}
    # 获取视频的cid,title
    html = requests.get(start_url, headers=headers).json()
    data = html['data']
    atitle = re.sub(r'[/\\:*?"<>|]', '', data['title'].replace(' ', ''))
    mylogger.info('[do_prepare] 视频的aid:{}\n[do_prepare] 视频的总标题:{}'.format(aid, atitle))

    cid_list = []
    if '?p=' in inputstart:
        # 单独下载分P视频中的一集
        p = re.search(r'\?p=(\d+)', inputstart).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        # 如果p不存在就是全集下载
        cid_list = data['pages']

    for item in cid_list:
        cid = str(item['cid'])
        # 处理视频名称
        pname = item['part']
        pname = re.sub(r'[/\\:*?"<>|]', '', pname.replace(' ', ''))  # 替换为空的

        # 秒数转成时分秒
        m, s = divmod(item['duration'], 60)
        h, m = divmod(m, 60)
        duration = '{}:{}:{}'.format(h, m, s)
        # 获得视频的大小以及下载地址
        purl = start_url + "/?p=" + str(item['page'])
        down_url_list, size_list = get_video_url(cid, purl, qn)
        total_size = 0
        for size in size_list:
            total_size += size

        # subprocess中的命令中不支持中文路径，所以视频文件夹路径暂时使用P001这种方式
        page = 'P{:0>3}'.format(item['page'])
        video_dict = dict(cid=cid, pname=pname, page=page, size=format_size(total_size),
                          duration=duration, purl=purl, down_url_list=down_url_list)
        result_list.append(video_dict)

        mylogger.info('[{}视频的cid]:{}\n[{}视频的名称]:{}\n[{}视频的大小]:{}\n[{}视频的时长]:{}\n[{}下载地址]:{}'.format
                      (page, cid, page, pname, page, format_size(total_size), page, duration, page, down_url_list))

    mylogger.info('[do_prepare] end!')
    return result_list


if __name__ == '__main__':
    mylogger = Logger(logger='bilibili').getlog()
    """
    qn参数就是视频清晰度 可选值：
    116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频)
    112: 高清1080P+ (hdflv2)(需要大会员)
    80: 高清1080P (flv)
    74: 高清720P60 (需要大会员)
    64: 高清720P (flv720)
    32: 清晰480P (flv480)
    16: 流畅360P (flv360)
    """
    av_lists = {
        # "樱兰高校单p分段": 'https://www.bilibili.com/video/av12084723',
        "高等数学": 'https://www.bilibili.com/video/av19027609',
        # "会长是女仆": 'https://www.bilibili.com/video/av16919357',
        "【韩语学习】零基础入门": 'https://www.bilibili.com/video/av52118083',
        "基础韩语语法60课——李思皎": 'https://www.bilibili.com/video/av50299922',
        "【史努比】【英语中字】": 'https://www.bilibili.com/video/av12022791',
        "【哆啦A梦】美版机器猫第一季26集合集【720P】": 'https://www.bilibili.com/video/av3343014',
        "【黑客基础】CMD命令/DOS命令学习": 'https://www.bilibili.com/video/av66315335',
        "【黑客基础】Windows/Powershell脚本学习": 'https://www.bilibili.com/video/av66327436',
        "144集英文动画童话故事高清合集": 'https://www.bilibili.com/video/av46525094',
        "15分钟复习完《综合素质》-2019年教师资格考试": 'https://www.bilibili.com/video/av68982183',
        "10分钟学会复习《教育知识与能力》": 'https://www.bilibili.com/video/av69717992',
        # "【650+】跟瑞秋老师学美语 | 316集起+英文字幕": 'https://www.bilibili.com/video/av53289663',
    }

    # start = input('请输入您要下载的B站av号或者视频链接地址:')
    # qn = input('请输入您要下载视频的清晰度,例：80(1080p:80;720p:64;480p:32;360p:16):')
    # start = 'https://www.bilibili.com/video/av16919357'
    qn = 80
    for key, value in av_lists.items():
        if value.isdigit():
            # 如果输入的是av号
            # 获取cid的api, 传入aid即可
            aid = value
        else:
            # 如果输入的是url (eg: https://www.bilibili.com/video/av46958874/)
            aid = re.search(r'/av(\d+)/*', value).group(1)

        # 创建文件夹,存放下载的视频
        down_video_path = os.path.join("d:\\", 'bilibili_video', aid)
        if not os.path.exists(down_video_path):
            os.makedirs(down_video_path)

        results = do_prepare(value, qn, aid)
        # start_download(results, down_video_path)

        page_list = []
        pname_list = []
        for result in results:
            page_list.append(result['page'])
            pname_list.append(result['pname'])
        concat_video(page_list, down_video_path, pname_list)

    # 如果是windows系统，下载完成后打开下载目录
    # if sys.platform.startswith('win'):
    #     os.startfile(down_video_path)

