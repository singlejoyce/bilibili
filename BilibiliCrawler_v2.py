import hashlib
import json
import os
import re
import sys
from datetime import datetime
import time
import urllib.request
import requests
import multiprocessing
from multiprocessing import Queue


class BilibiliCrawler:
    def __init__(self, down_path):
        # 初始化
        self.downVideoPath = down_path

    # 访问API地址
    def get_play_list(self, start_url, cid, quality):
        entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
        appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
        params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
        chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
        url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
        headers = {
            'Referer': start_url,  # 注意加上referer
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        # print(url_api)
        html = requests.get(url_api, headers=headers).json()
        # print(json.dumps(html))
        video_list = []
        for i in html['durl']:
            video_list.append(i['url'])
        # print(video_list)
        return video_list

    # 字节bytes转化K\M\G
    def format_size(self, bytes):
        try:
            bytes = float(bytes)
            kb = bytes / 1024
        except:
            print("传入的字节格式不对")
            return "Error"
        if kb >= 1024:
            M = kb / 1024
            if M >= 1024:
                G = M / 1024
                return "%.3fG" % (G)
            else:
                return "%.3fM" % (M)
        else:
            return "%.3fK" % (kb)

    def Schedule_cmd(self, blocknum, blocksize, totalsize):
        speed = (blocknum * blocksize) / (time.time() - start_time)
        # speed_str = " Speed: %.2f" % speed
        speed_str = " Speed: %s" % self.format_size(speed)
        recv_size = blocknum * blocksize

        # 设置下载进度条
        f = sys.stdout
        pervent = recv_size / totalsize
        percent_str = "%.2f%%" % (pervent * 100)
        n = round(pervent * 50)
        s = ('#' * n).ljust(50, '-')
        f.write(percent_str.ljust(8, ' ') + '[' + s + ']' + speed_str)
        f.flush()
        # time.sleep(0.1)
        f.write('\r')

    # 下载视频
    def down_video(self, video_list, aid, title, start_url, page):
        num = 1
        print('[正在下载P{}段视频,请稍等...]:'.format(page) + title)
        # currentVideoPath = os.path.join(sys.path[0], 'bilibili_video', title)  # 当前目录作为下载目录
        currentVideoPath = os.path.join(self.downVideoPath, aid, title)  # 当前目录作为下载目录
        # 创建文件夹存放下载的视频
        if not os.path.exists(currentVideoPath):
            os.makedirs(currentVideoPath)
        for i in video_list:
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
            if len(video_list) > 1:
                urllib.request.urlretrieve(url=i,
                                           filename=os.path.join(currentVideoPath, r'{}-{}.flv'.format(title, num)),
                                           reporthook=self.Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
            else:
                urllib.request.urlretrieve(url=i, filename=os.path.join(currentVideoPath, r'{}.flv'.format(title)),
                                           reporthook=self.Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
            num += 1

    def start(self, aid):
        # qn参数就是视频清晰度
        # 可选值：
        # 116: 高清1080P60 (需要带入大会员的cookie中的SESSDATA才行,普通用户的SESSDATA最多只能下载1080p的视频)
        # 112: 高清1080P+ (hdflv2) (需要大会员)
        # 80: 高清1080P (flv)
        # 74: 高清720P60 (需要大会员)
        # 64: 高清720P (flv720)
        # 32: 清晰480P (flv480)
        # 16: 流畅360P (flv360)
        qn = 80
        # 得到对应的flv下载地址
        start_url = 'https://api.bilibili.com/x/web-interface/view?aid={}'.format(aid)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/55.0.2883.87 Safari/537.36 '
        }
        html = requests.get(start_url, headers=headers).json()
        data = html['data']
        cid_list = data['pages']
        print("%s: av:%s 数据获取中..." % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), aid))
        for item in cid_list:
            cid = str(item['cid'])
            title = item['part']
            title = re.sub(r'[/\\:*?"<>|]', '', title)  # 替换为空的
            page = str(item['page'])
            start_url = start_url + "/?p=" + page
            video_list = self.get_play_list(start_url, cid, qn)
            start_time = time.time()
            self.down_video(video_list, aid, title, start_url, page)
            end_time = time.time()  # 结束时间
            print('[视频]%s:下载总耗时%.2f秒,约%.2f分钟' % (title, end_time - start_time, int(end_time - start_time) / 60))

        # # 如果是windows系统，下载完成后打开下载目录
        # currentVideoPath = os.path.join(self.downVideoPath, aid)  # 当前目录作为下载目录
        # if sys.platform.startswith('win'):
        #     os.startfile(currentVideoPath)


if __name__ == '__main__':
    start_time = time.time()
    downpath = 'D:\\bilibili-video\\'
    # avlist = ['39031994', '34904005']
    avlist = ['70945937', '70851464', '68532915']
    for i in avlist:
        bilibili = BilibiliCrawler(downpath)
        bilibili.start(i)

