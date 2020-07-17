import os
import shutil
from os.path import join, getsize
import re
import subprocess

import sys


def move(path, newpath, file_type):
    for root, dirs, files in os.walk(path):
        for i in range(len(files)):
            if files[i].endswith(file_type):
                file_path = root + '\\' + files[i]
                newpath = newpath + '\\' + files[i]
                shutil.move(file_path, newpath)


def getdirsize(path):
    size = 0
    for root, dirs, files in os.walk(path):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def getfilesize(path):
    for root, dirs, files in os.walk(path):
        sizelist = [size_format(getsize(join(root, file))) for file in files]
        file_dict = dict(zip(files, sizelist))
        return file_dict


def renamefile(path):
    for file in os.listdir(path):
        # [\u4e00-\u9fa5]中文范围
        name = re.split(r'(\W*[\u4e00-\u9fa5])', file.replace(' ', ''))
        new1 = str(name[0].split('.')[0])
        new2 = str(name[0].split('.')[1])
        if len(new1) == 1:
            new1 = '0' + new1
        if len(new2) == 1:
            new2 = '0' + new2
        name[0] = new1 + '.' + new2
        new_name = ''.join(name)
        os.rename(os.path.join(path, file), os.path.join(path, new_name))


def size_format(size):
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


# new_path = 'D:\\bilibili_video\\test'
# old_path = 'D:\\bilibili_video\\39031994'
# old_path2 = 'D:\\bilibili_video\\34904005'
# ftype = '.flv'
# move(old_path, new_path, ftype)
# print(getfilesize(old_path2))

# format操作示例
# print('{:0>3}.flv'.format(2))
# # 002.flv
# print('{:08.4f}'.format(6.4))
# # 006.4000
# print('{:.8f}'.format(6.4))
# # 6.40000000
# print('{:0>8}'.format('189'))
# # 00000189
# print('{:_>8}'.format('189'))
# # _____189
import locale
ffmpeg = 'D:/ffmpeg-20191022-0b8956b-win64-static/bin/ffmpeg'
dir1 = 'd:/bilibili_video/19027609/001.实数集/filelist.txt'
dir2 = 'd:/bilibili_video/19027609/001.实数集/001.实数集.mp4'
cmd = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', dir1, '-c', 'copy', dir2]
# proc = subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
cmd2 = "{} -y -f concat -safe 0 -i {} -c copy {}".format(ffmpeg, dir1, dir2)
print(cmd2)
import locale
cmd3 = cmd2.encode(locale.getdefaultlocale()[1])
print(cmd3)
subprocess.Popen(cmd3, shell=True)
