import os
import shutil
from os.path import join, getsize
import re
import aiohttp

from bilibili_download import download_from_url


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


new_path = 'D:\\bilibili_video\\test'
old_path = 'D:\\bilibili_video\\39031994'
old_path2 = 'D:\\bilibili_video\\34904005'

ftype = '.flv'


# move(old_path, new_path, ftype)
# print(getfilesize(old_path2))
