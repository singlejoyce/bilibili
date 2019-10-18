import json
import os
import sys
from datetime import datetime
import requests
import multiprocessing
from multiprocessing import Queue


class BilibiliCrawler:
    def __init__(self, aid, qn, down_path):
        # ��ʼ��
        self.down_path = os.path.join(down_path, aid)
        if not os.path.exists(down_path):
            os.mkdir(down_path)
        self.aid = aid
        self.percent = 0.0
        self.resultList = []
        self.chunk_size = 1024
        self.qn = qn
        self.cid_url = 'https://api.bilibili.com/x/player/pagelist?aid={}&jsonp=jsonp'
        self.flv_url = 'https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn={}&type=&otype=json'
        self.headers1 = {
            'host': 'api.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3751.400',
            'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;',
        }
        self.headers2 = {
            'host': '',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/video/ac{}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3722.400 QQBrowser/10.5.3751.400',
            'Cookie': 'SESSDATA = 0da81169%2C1571985072%2Cae38dc91;',
        }

    def get_cid(self, url):
        # ��ȡAV�����е�p����Ϣ
        try:
            print("%s: get_cid���ݻ�ȡ��..." % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            data = requests.get(url, headers=self.headers1).json()
            detail_list = data['data']
            for detail in detail_list:
                av_dict = dict(cid=detail['cid'], name=detail['part'], duration=detail['duration'], flv_down_url='')
                self.resultList.append(av_dict)
        except:
            print("pagelist ��ȡʧ��")

    def get_flv_down_url(self):
        # �õ���Ӧ��flv���ص�ַ
        self.get_cid(self.cid_url.format(self.aid))
        print("%s: av:%s get_flv_down_url���ݻ�ȡ��..." % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.aid))
        for i in range(len(self.resultList)):
            cid = self.resultList[i]['cid']
            duration = self.resultList[i]['duration']
            data = requests.get(self.flv_url.format(self.aid, cid, self.qn), headers=self.headers1).json()
            durl = data['data']['durl'][0]
            self.resultList[i]['flv_down_url'] = durl['url']
            self.headers2['host'] = durl['url'].split('/')[2]
            minutes = int(duration / 60)
            seconds = int(duration - minutes * 60.0)
            self.resultList[i]['duration'] = '{}m{}s'.format(minutes, seconds)

    def show_progress(self, queue):
        while True:
            per = queue.get()
            if self.percent != per:
                # print('  [%s ���ؽ���]:%.1f%%' % (datetime.now().strftime("%Y%m%d %H:%M:%S"), per) + '\r')
                print(' [%s ���ؽ���]: %s' % (datetime.now().strftime("%Y%m%d %H:%M:%S"), per) + '%\r')
                self.percent = per

    def download(self, queue, url, filename='None.flv'):
        # ����
        size = 0
        response = requests.get(url, headers=self.headers2, stream=True, verify=False)
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        if response.status_code == 200:
            sys.stdout.write(' [�ļ���С]:%0.2f MB\n' % (content_size / chunk_size / 1024))
            filename = os.path.join(self.down_path, filename)
            with open(filename, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    file.flush()
                    # per = float('%.1f' % float(size / content_size * 100))
                    per = "%.2f%%" % (size / content_size * 100)
                    queue.put(per)
        else:
            print('%s ���س���.' % datetime.now().strftime("%Y%m%d %H:%M:%S"))

    def startDownload(self, data):
        # �����̴���my_queue�������������ӽ��̣�
        my_queue = Queue()
        down_url = data['flv_down_url']
        if data['name'] != '':
            filename = data['name'].replace(' ', '_') + '.flv'
            p1 = multiprocessing.Process(target=self.download, args=(my_queue, down_url, filename))
        else:
            p1 = multiprocessing.Process(target=self.download, args=(my_queue, down_url))
        p2 = multiprocessing.Process(target=self.show_progress, args=(my_queue,))
        # �����ӽ���p1����ʼ����:
        p1.start()
        # �����ӽ���p2����ʼ��ӡ���ؽ���:
        p2.start()
        # �ȴ�p1����:
        p1.join()
        # p2����������ѭ�����޷��ȴ��������ֻ��ǿ����ֹ:
        p2.terminate()

    # ����д��json����json�ļ�����ʾ"\u6731\u5fb7\u57f9",�������ġ�
    # �������������ensure_ascii = False
    # ��Ŀ��json�ļ�����Ϊ��ʱ������json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
    # �������������һ���쳣
    def saveJsonFile(self, source, file_path):
        print("%s: json�ļ�д����..." % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            with open(file_path, 'w', encoding='utf-8') as f_obj:
                json.dump(source, f_obj, ensure_ascii=False, indent=4)
        except json.decoder.JSONDecodeError:
            print("json�ļ�����Ϊ��.")
        print("%s: json�ļ�д�����." % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def start(self):
        # ���ϸ�av�Ľ����Ϣ�б����
        self.resultList.clear()
        # ��ȡ��Ƶ���ص�ַ
        self.get_flv_down_url()
        # �����������Ӧ��json�ļ���
        self.saveJsonFile(self.resultList, self.down_path + "\\result.json")
        # ��ʼ����
        for data in self.resultList:
            self.startDownload(data)


if __name__ == '__main__':
    downpath = 'D:\\bilibili-down\\'
    # avlist = ['39031994', '34904005']
    avlist = ['70945937', '70851464']
    for i in avlist:
        bilibili = BilibiliCrawler(i, 80, downpath)
        bilibili.start()