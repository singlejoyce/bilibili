# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2019/04/16--17:12
import json
from datetime import datetime

import aiohttp
from tqdm import tqdm

__author__ = 'Henry'

'''
项目: B站视频下载
版本2: 无加密API版,但是需要加入登录后cookie中的SESSDATA字段,才可下载720p及以上视频
API:
1.获取cid的api为 https://api.bilibili.com/x/web-interface/view?aid=47476691 aid后面为av号
2.下载链接api为 https://api.bilibili.com/x/player/playurl?avid=44743619&cid=78328965&qn=32 cid为上面获取到的 avid为输入的av号 qn为视频质量
注意:
但是此接口headers需要加上登录后'Cookie': 'SESSDATA=3c5d20cf%2C1556704080%2C7dcd8c41' (30天的有效期)(因为现在只有登录后才能看到720P以上视频了)
不然下载之后都是最低清晰度,哪怕选择了80也是只有480p的分辨率!!
20190422 - 增加多P视频单独下载其中一集的功能
'''

import os
import sys

import re
import requests
import time
import urllib.request


def format_size(size):
    if size < 1000:
        return '%i' % size + 'size'
    elif 1000 <= size < 1000000:
        return '%.1f' % float(size / 1000) + 'KB'
    elif 1000000 <= size < 1000000000:
        return '%.1f' % float(size / 1000000) + 'MB'
    elif 1000000000 <= size < 1000000000000:
        return '%.1f' % float(size / 1000000000) + 'GB'
    elif 1000000000000 <= size:
        return '%.1f' % float(size / 1000000000000) + 'TB'


# 访问API地址
def get_play_list(aid, cid, quality):
    url_api = 'https://api.bilibili.com/x/player/playurl?cid={}&avid={}&qn={}'.format(cid, aid, quality)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                      'Safari/537.36',
        'Cookie': 'SESSDATA=aa15d6af%2C1560734457%2Ccc8ca251',  # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    res = requests.get(url_api, headers=header).json()
    # video_url_list = []
    # size_list = []
    # for i in html['data']['durl']:
    #     video_url_list.append(i['url'])
    #     size_list.append(i['size'])
    # return dict(downurl=video_url_list, size=size_list)
    video_url = res['data']['durl'][0]['url']
    video_size = res['data']['durl'][0]['size']
    video_size = format_size(video_size)
    return video_url, video_size


'''
 urllib.urlretrieve 的回调函数：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''


def Schedule_cmd(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time2)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    pervent = recv_size / totalsize
    totalsize_str = " totalsize: %s\r" % format_size(totalsize)
    percent_str = "%.2f%%" % (pervent * 100)
    # n = round(pervent * 50)
    # s = ('#' * n).ljust(50, '-')
    # print(percent_str.ljust(8, ' ') + '[' + s + ']' + speed_str + totalsize_str)
    print(percent_str.ljust(8, ' ') + speed_str + totalsize_str)


def download_from_url(url, file, start_url):
    headers = {'host': url.split('/')[2],
               'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.5',
               'Origin': 'https://www.bilibili.com',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive',
               'Referer': start_url,
               'Range': 'bytes=0-',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3751.400',
               'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;'}
    response = requests.get(url, headers=headers, stream=True, verify=False)
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
    req = requests.get(url, headers=headers, stream=True)
    with (open(file, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


async def fetch(session, url, dst, pbar=None, headers=None):
    if headers:
        async with session.get(url, headers=headers) as req:
            with(open(dst, 'ab')) as f:
                while True:
                    chunk = await req.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    pbar.update(1024)
            pbar.close()
    else:
        async with session.get(url) as req:
            return req


async def async_download_from_url(url, file, start_url):
    """异步"""
    headers = {'host': url.split('/')[2],
               'Accept': '*/*',
               'Accept-Language': 'en-US,en;q=0.5',
               'Origin': 'https://www.bilibili.com',
               'Accept-Encoding': 'gzip, deflate, br',
               'Connection': 'keep-alive',
               'Referer': start_url,
               'Range': 'bytes=0-',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3751.400',
               'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;'}
    async with aiohttp.TCPConnector(limit=300, force_close=True, enable_cleanup_closed=True) as tc:
        async with aiohttp.ClientSession(connector=tc) as session:
            req = await fetch(session, url, file)
            file_size = int(req.header['content-length'])
            if os.path.exists(file):
                first_byte = os.path.getsize(file)
            else:
                first_byte = 0
            if first_byte >= file_size:
                return file_size
            headers['Range'] = f"bytes={first_byte}-{file_size}"
            pbar = tqdm(total=file_size, initial=first_byte, unit='B',
                        unit_scale=True, desc=file)
            await fetch(session, url, file, pbar=pbar, headers=headers)


# 下载视频
def down_video(video_url, title, start_url, page, savepath):
    print('[正在下载P{}段视频,请稍等...]:'.format(page) + title)
    opener = urllib.request.build_opener()
    # 请求头
    opener.addheaders = [
        # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
        ('Referer', start_url),  # 注意修改referer,必须要加的!
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),

    ]
    urllib.request.install_opener(opener)
    # 开始下载
    filename = os.path.join(savepath, r'{}.flv'.format(title))
    try:
        urllib.request.urlretrieve(url=video_url, filename=filename, reporthook=Schedule_cmd)
    except:
        print('[视频下载失败]:' + title)


# 中文写入json，但json文件中显示"\u6731\u5fb7\u57f9",不是中文。
# 解决方法：加入ensure_ascii = False
# 当目标json文件内容为空时，出现json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
# 解决方法：新增一个异常
def saveJsonFile(self, source, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
    print("%s: json文件写入中..." % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        with open(file_path, 'w', encoding='utf-8') as f_obj:
            json.dump(source, f_obj, ensure_ascii=False, indent=4)
    except json.decoder.JSONDecodeError:
        print("json文件内容为空.")
    print("%s: json文件写入完成." % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def format_title(title):
    """针对39031994这个aid的title进行特殊处理"""
    name = re.split(r'(\W*[\u4e00-\u9fa5])', title.replace(' ', ''))
    new1 = str(name[0].split('.')[0])
    new2 = str(name[0].split('.')[1])
    if len(new1) == 1:
        new1 = '0' + new1
    if len(new2) == 1:
        new2 = '0' + new2
    name[0] = new1 + '.' + new2
    new_name = ''.join(name)
    return new_name


if __name__ == '__main__':
    # 用户输入av号或者视频链接地址
    print('*' * 30 + 'B站视频下载小助手' + '*' * 30)
    start = input('请输入您要下载的B站av号或者视频链接地址:')
    if start.isdigit():
        # 如果输入的是av号
        # 获取cid的api, 传入aid即可
        aid = start
    else:
        # 如果输入的是url (eg: https://www.bilibili.com/video/av46958874/)
        aid = re.search(r'/av(\d+)/*', start).group(1)
    start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + aid
    # qn参数就是视频清晰度 可选值：
    # 116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频)
    # 112: 高清1080P+ (hdflv2)(需要大会员)
    # 80: 高清1080P (flv)
    # 74: 高清720P60 (需要大会员)
    # 64: 高清720P (flv720)
    # 32: 清晰480P (flv480)
    # 16: 流畅360P (flv360)
    # print('请输入您要下载视频的清晰度(1080p60:116;1080p+:112;1080p:80;720p60:74;720p:64;480p:32;360p:16; **注意:1080p+,1080p60,
    # 720p60,720p都需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频):')
    #  quality = input('请填写116或112或80或74或64或32或16:')
    quality = 80
    # 获取视频的cid,title
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                      'Safari/537.36 '
    }
    html = requests.get(start_url, headers=headers).json()
    data = html['data']
    cid_list = []
    if '?p=' in start:
        # 单独下载分P视频中的一集
        p = re.search(r'\?p=(\d+)', start).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        # 如果p不存在就是全集下载
        cid_list = data['pages']
    # print(cid_list)
    # 创建文件夹存放下载的视频
    down_video_path = os.path.join("d:\\", 'bilibili_video', aid)  # 当前目录作为下载目录
    if not os.path.exists(down_video_path):
        os.makedirs(down_video_path)
    start_time1 = time.time()
    for item in cid_list:
        cid = str(item['cid'])
        title = item['part']
        # title = re.sub(r'[/\\:*?"<>|]', '', title.replace(' ', ''))  # 替换为空的
        title = format_title(title)
        # 秒数转成时分秒
        m, s = divmod(item['duration'], 60)
        h, m = divmod(m, 60)
        print("%02d:%02d:%02d" % (h, m, s))
        duration = '{}:{}:{}'.format(h, m, s)
        page = str(item['page'])
        start_url = start_url + "/?p=" + page
        video_list = get_play_list(aid, cid, quality)
        size = video_list[1]
        downurl = video_list[0]
        print('[视频的cid]:' + cid)
        print('[视频的title]:' + title)
        print('[视频的size]:' + size)
        print('[视频的duration]:' + duration)
        print('[视频的downurl]:' + downurl)

        start_time2 = time.time()
        filename = os.path.join(down_video_path, r'{}.flv'.format(title))
        download_from_url(downurl, filename, start_url)
        # async_download_from_url(downurl, filename, start_url)
        # down_video(downurl, title, start_url, page, filename)
        print('[视频：%s]下载耗时%.2f秒,约%.2f分钟' % (title, time.time() - start_time2, int(time.time() - start_time2) / 60))

    print('下载总耗时%.2f秒,约%.2f分钟' % (time.time() - start_time1, int(time.time() - start_time1) / 60))

    # 如果是windows系统，下载完成后打开下载目录
    if sys.platform.startswith('win'):
        os.startfile(down_video_path)

        # 分P视频下载测试: https://www.bilibili.com/video/av19516333/
        # 50044420
        # 34904005
        # 39031994
