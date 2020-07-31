#!/usr/bin/env python
# -*- coding:utf-8 -*-

__all__ = ['netease_download']

from ..common import *
from ..common import print_more_compatible as print
from ..util import fs
from json import loads
import hashlib
import base64
import os
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TRCK, TCOP, TYER, TDRC, USLT

netease_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': '_ntes_nnid=769c1ff9d5294ef308057f1a185e2c28,1577249142312; _ntes_nuid=769c1ff9d5294ef308057f1a185e2c28; WM_TID=uxyRWSrnyrpEUQREAAJt%2Bh6LKUBVWk0k; _iuqxldmzr_=32; ntes_kaola_ad=1; JSESSIONID-WYYY=Ja0moAH7i5j64I8IVthkrbsxeoe4K36BoNmnoVktMF%2FQ7ITgNOe7ldUOpB0WWgQs8tzho2h40miu9aJTBGUiPboFFn76hfKfS4Wcpi%2BA8jfnqAfdPhNJz6FUh2MVAWSfX9U4HZQ26fFi2KEYwYl%2BJ0BKYsnaba8HeTRvM%5CmmDibRqNXJ%3A1590632972384; WM_NI=6KWB1rzI7OwdnIVokMHMlbLyr6%2BurXLwrobbyfeNPIz2%2BTVqolm61YoxDtNiBNh%2B0TiOk4E8AeA9ADPljiLelP%2B3YMfXhaXL%2BKnA0EN2iszE3SSKKyBpBEydoLnHwWKgYzk%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eedaf6478fb7ac85b2448dbc8ea2c44b978f8faef1608cba99a6d16fa8908694b22af0fea7c3b92af69599a3b47aba97f9b0f670ae979a90ea478c93a483cf73b2eae596f15490a9be90e16abbbaabafd343baeee5b5d57badb4a3d7b453ada88c95cd638292a8ccb360ab91a5d5c83483bb8fdac45094b4a68acf6fb090e5d4dc47a688a882db48e995a2a2b34f8eeea794f94ff18d9dacca7382b08ea6fc70ad94a2a9f65d89b9979bea37e2a3; MUSIC_U=edd4f7453a44f3b6cacff1ec272675b38672ffefed2613720ee2aef326c85ee133a649814e309366; __remember_me=true; __csrf=a2016837a0b1be13b68d2963db3aa726',
    'Referer': 'https://music.163.com/',
}

def netease_hymn():
    return """
    player's Game Over,
    u can abandon.
    u get pissed,
    get pissed,
    Hallelujah my King!
    errr oh! fuck ohhh!!!!
    """


# 格式化字符串，去掉非法字符
# 部分日文歌名及歌手包含特殊字符需要处理，否则无法正常下载
def formatString(string):
    return re.sub(r'[\\/:#*?"<>|\r\n]+', '', string)


# 时间戳格式转换
def stamp_to_time(stamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(str(stamp)[0:10]))) + '.' + str(stamp)[10:]

# 设置歌曲详细信息
def setSongInfo(song_path, lyr_path, pic_path, song_info, media_type='mp3'):
    lyrics = open(lyr_path, encoding='utf-8').read().strip()
    # try to find the right encoding
    for enc in ('utf8', 'iso-8859-1', 'iso-8859-15', 'cp1252', 'cp1251', 'latin1'):
        try:
            lyrics = lyrics.decode(enc)
            print(enc, )
            break
        except:
            pass

    if media_type == 'mp3':
        # 用eyed3库只支持英文歌名，对utf-8格式的文件无法修改；所以使用mutagen库替代修改mp3信息
        # 传入mp3、jpg的url路径以及其他字符串
        tags = ID3(song_path)
        tags.update_to_v23()  # 把可能存在的旧版本升级为2.3
        # 插入歌名
        tags['TIT2'] = TIT2(encoding=3, text=[song_info['name']])
        # 插入歌曲艺术家

        tags['TPE1'] = TPE1(encoding=3, text=[song_info['artist']])
        # 插入专辑名称
        tags['TALB'] = TALB(encoding=3, text=[song_info['albumName']])
        # 插入专辑公司
        # tags['TCOP'] = TCOP(encoding=3, text=[music_info['Company']])
        # 插入声道数
        tags['TRCK'] = TRCK(encoding=3, text=[song_info['trackNumber']])
        # 插入发行时间

        tags['TYER'] = TYER(encoding=3, text=[song_info['publishYear']])
        tags["TDRC"] = TDRC(encoding=3, text=song_info['publishYear'])
        # 插入专辑图片
        # response = urllib.request.urlopen(mp3_header_info['albumPicDownUrl'])
        # tags['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=response.data)
        with open(pic_path, 'rb') as img:
            tags['APIC'] = APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=img.read())
        # 插入歌词
        # remove old unsychronized lyrics
        if len(tags.getall(u"USLT::'en'")) != 0:
            mylogger.info("Removing Lyrics.")
            tags.delall(u"USLT::'en'")
            tags.save()

        # tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
        # apparently the description is important when more than one
        # USLT frames are present
        tags[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
        tags.save()

def netease_cloud_music_download(url, output_dir='.', merge=True, info_only=False, **kwargs):
    rid = match1(url, r'\Wid=(.*)')
    if rid is None:
        rid = match1(url, r'/(\d+)/?')
    if "album" in url:
        j = loads(get_content("http://music.163.com/api/album/%s?id=%s&csrf_token=" % (rid, rid), headers=netease_header))

        artist_name = j['album']['artists'][0]['name']
        album_name = j['album']['name'].strip()
        new_dir = output_dir + '/' + fs.legitimize("%s - %s" % (artist_name, album_name))
        if not info_only:
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
            cover_url = j['album']['picUrl']
            download_urls([cover_url], "cover", "jpg", 0, new_dir)

        for i in j['album']['songs']:
            artist = '&'.join([formatString(artist['name']) for artist in i['artists']])
            title = "%s - %s" % (artist, i['name'])
            netease_song_download(i, title, output_dir=new_dir, info_only=info_only)
            try: # download lyrics
                assert kwargs['caption']
                l = loads(get_content("http://music.163.com/api/song/lyric/?id=%s&lv=-1&csrf_token=" % i['id'], headers=netease_header))
                netease_lyric_download(i, l["lrc"]["lyric"], title, output_dir=new_dir, info_only=info_only)   
                download_urls([i['album']['picUrl']], title, "jpg", 0, new_dir)
                mp3_path = os.path.join(new_dir, '%s.mp3' % get_filename(title))
                lrc_path = os.path.join(new_dir, '%s.lrc' % get_filename(title))
                pic_path = os.path.join(new_dir, '%s.jpg' % get_filename(title))
                song_info = dict(name=formatString(i['name']), trackNumber=i['no'],
                                 artist=artist, albumName=i['album']['name'],
                                 publishYear=stamp_to_time(i['album']['publishTime'])[:4])
                setSongInfo(mp3_path, lrc_path, pic_path, song_info)
                # if os.path.exists(lrc_path) or os.path.exists(pic_path):
                #     os.remove(lrc_path)
                #     os.remove(pic_path)
            except: pass

    elif "artist" in url:
        j = loads(get_content("http://music.163.com/api/cloudsearch/pc?s=%s&type=1&limit=%s&total=true" % (rid, 50), headers=netease_header))
        new_dir = output_dir + '/' + fs.legitimize(j['result']['songs'][0]['ar'][0]['name'])
        if not info_only:
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        for i in j['result']['songs']:
            artist = '&'.join([formatString(artist['name']) for artist in i['ar']])
            title = "%s - %s" % (artist, i['name'])
            netease_song_download(i, title, output_dir=new_dir, info_only=info_only)
            try: # download lyrics
                assert kwargs['caption']
                l = loads(get_content("http://music.163.com/api/song/lyric/?id=%s&lv=-1&csrf_token=" % i['id'], headers=netease_header))
                netease_lyric_download(i, l["lrc"]["lyric"], title, output_dir=new_dir, info_only=info_only)
                download_urls([i['al']['picUrl']], title, "jpg", 0, new_dir)
                mp3_path = os.path.join(new_dir, '%s.mp3' % get_filename(title))
                lrc_path = os.path.join(new_dir, '%s.lrc' % get_filename(title))
                pic_path = os.path.join(new_dir, '%s.jpg' % get_filename(title))
                song_info = dict(name=formatString(i['name']), trackNumber=i['no'],
                                 artist=artist,
                                 albumName='&'.join([formatString(alia) for alia in i['alia']]),
                                 publishYear=stamp_to_time(i['publishTime'])[:4])
                setSongInfo(mp3_path, lrc_path, pic_path, song_info)
                # if os.path.exists(lrc_path) or os.path.exists(pic_path):
                #     os.remove(lrc_path)
                #     os.remove(pic_path)
            except: pass

    elif "playlist" in url:
        j = loads(get_content("http://music.163.com/api/playlist/detail?id=%s&csrf_token=" % rid, headers=netease_header))

        new_dir = output_dir + '/' + fs.legitimize(j['result']['name'])
        if not info_only:
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
            cover_url = j['result']['coverImgUrl']
            download_urls([cover_url], "cover", "jpg", 0, new_dir)
        
        prefix_width = len(str(len(j['result']['tracks'])))
        for n, i in enumerate(j['result']['tracks']):
            playlist_prefix = '%%.%dd_' % prefix_width % n
            artist = '&'.join([formatString(artist['name']) for artist in i['artists']])
            title = "%s - %s" % (artist, i['name'])
            netease_song_download(i, title, output_dir=new_dir, info_only=info_only, playlist_prefix=playlist_prefix)
            try: # download lyrics
                assert kwargs['caption']
                l = loads(get_content("http://music.163.com/api/song/lyric/?id=%s&lv=-1&csrf_token=" % i['id'], headers=netease_header))
                netease_lyric_download(i, l["lrc"]["lyric"], title, output_dir=new_dir, info_only=info_only)
                download_urls([i['album']['picUrl']], title, "jpg", 0, new_dir)
                mp3_path = os.path.join(new_dir, '%s.mp3' % get_filename(title))
                lrc_path = os.path.join(new_dir, '%s.lrc' % get_filename(title))
                pic_path = os.path.join(new_dir, '%s.jpg' % get_filename(title))
                song_info = dict(name=formatString(i['name']), trackNumber=i['no'],
                                 artist=artist, albumName=i['album']['name'],
                                 publishYear=stamp_to_time(i['album']['publishTime'])[:4])
                setSongInfo(mp3_path, lrc_path, pic_path, song_info)
                # if os.path.exists(lrc_path) or os.path.exists(pic_path):
                #     os.remove(lrc_path)
                #     os.remove(pic_path)
            except: pass

    elif "song" in url:
        j = loads(get_content("http://music.163.com/api/song/detail/?id=%s&ids=[%s]&csrf_token=" % (rid, rid), headers=netease_header))
        artist = '&'.join([formatString(artist['name']) for artist in j["songs"][0]['artists']])
        title = "%s - %s" % (artist, j["songs"][0]['name'])
        netease_song_download(j["songs"][0], title, output_dir=output_dir, info_only=info_only)
        try: # download lyrics
            assert kwargs['caption']
            l = loads(get_content("http://music.163.com/api/song/lyric/?id=%s&lv=-1&csrf_token=" % rid, headers=netease_header))
            netease_lyric_download(j["songs"][0], l["lrc"]["lyric"], title, output_dir=output_dir, info_only=info_only)
            download_urls([j["songs"][0]['album']['picUrl']], title, "jpg", 0, output_dir)
            mp3_path = os.path.join(output_dir, '%s.mp3' % get_filename(title))
            lrc_path = os.path.join(output_dir, '%s.lrc' % get_filename(title))
            pic_path = os.path.join(output_dir, '%s.jpg' % get_filename(title))
            song_info = dict(name=formatString(j["songs"][0]['name']), trackNumber=j["songs"][0]['no'],
                             artist=artist, albumName=j["songs"][0]['album']['name'],
                             publishYear=stamp_to_time(j["songs"][0]['album']['publishTime'])[:4])
            setSongInfo(mp3_path, lrc_path, pic_path, song_info)
            # if os.path.exists(lrc_path) or os.path.exists(pic_path):
            #     os.remove(lrc_path)
            #     os.remove(pic_path)
        except: pass

    elif "program" in url:
        j = loads(get_content("http://music.163.com/api/dj/program/detail/?id=%s&ids=[%s]&csrf_token=" % (rid, rid), headers=netease_header))

        netease_song_download(j["program"]["mainSong"], j["program"]["mainSong"]['name'], output_dir=output_dir, info_only=info_only)

    elif "radio" in url:
        j = loads(get_content("http://music.163.com/api/dj/program/byradio/?radioId=%s&ids=[%s]&csrf_token=" % (rid, rid), headers=netease_header))
        for i in j['programs']:
            netease_song_download(i["mainSong"], i["mainSong"]['name'], output_dir=output_dir, info_only=info_only)

    elif "mv" in url:
        j = loads(get_content("http://music.163.com/api/mv/detail/?id=%s&ids=[%s]&csrf_token=" % (rid, rid), headers=netease_header))
        netease_video_download(j['data'], output_dir=output_dir, info_only=info_only)

def netease_lyric_download(song, lyric, title, output_dir='.', info_only=False, playlist_prefix=""):
    if info_only: return

    # title = "%s%s. %s" % (playlist_prefix, song['position'], song['name'])
    filename = '%s.lrc' % get_filename(title)
    print('Saving %s ...' % filename, end="", flush=True)
    with open(os.path.join(output_dir, filename),
              'w', encoding='utf-8') as x:
        x.write(lyric)
        print('Done.')


def netease_video_download(vinfo, output_dir='.', info_only=False):
    title = "%s - %s" % (vinfo['name'], vinfo['artistName'])
    url_best = sorted(vinfo["brs"].items(), reverse=True,
                      key=lambda x: int(x[0]))[0][1]
    netease_download_common(title, url_best,
                            output_dir=output_dir, info_only=info_only)

def netease_song_download(song, title, output_dir='.', info_only=False, playlist_prefix=""):
    # title = "%s%s. %s" % (playlist_prefix, song['position'], song['name'])
    url_best = "http://music.163.com/song/media/outer/url?id=" + \
        str(song['id']) + ".mp3"
    '''
    songNet = 'p' + song['mp3Url'].split('/')[2][1:]

    if 'hMusic' in song and song['hMusic'] != None:
        url_best = make_url(songNet, song['hMusic']['dfsId'])
    elif 'mp3Url' in song:
        url_best = song['mp3Url']
    elif 'bMusic' in song:
        url_best = make_url(songNet, song['bMusic']['dfsId'])
    '''
    netease_download_common(title, url_best,
                            output_dir=output_dir, info_only=info_only)

def netease_download_common(title, url_best, output_dir, info_only):
    songtype, ext, size = url_info(url_best)
    if size is not None:
        print_info(site_info, title, songtype, size)
        if not info_only:
            download_urls([url_best], title, ext, size, output_dir)


def netease_download(url, output_dir = '.', merge = True, info_only = False, **kwargs):
    if "163.fm" in url:
        url = get_location(url)
    if "music.163.com" in url:
        netease_cloud_music_download(url, output_dir, merge, info_only, **kwargs)
    else:
        html = get_decoded_html(url)

        title = r1('movieDescription=\'([^\']+)\'', html) or r1('<title>(.+)</title>', html)

        if title[0] == ' ':
            title = title[1:]

        src = r1(r'<source src="([^"]+)"', html) or r1(r'<source type="[^"]+" src="([^"]+)"', html)

        if src:
            url = src
            _, ext, size = url_info(src)
            #sd_url = r1(r'(.+)-mobile.mp4', src) + ".flv"
            #hd_url = re.sub('/SD/', '/HD/', sd_url)

        else:
            url = (r1(r'["\'](.+)-list.m3u8["\']', html) or r1(r'["\'](.+).m3u8["\']', html)) + ".mp4"
            _, _, size = url_info(url)
            ext = 'mp4'

        print_info(site_info, title, ext, size)
        if not info_only:
            download_urls([url], title, ext, size, output_dir = output_dir, merge = merge)


def encrypted_id(dfsId):
    x = [ord(i[0]) for i in netease_hymn().split()]
    y = ''.join([chr(i - 61) if i > 96 else chr(i + 32) for i in x])
    byte1 = bytearray(y, encoding='ascii')
    byte2 = bytearray(str(dfsId), encoding='ascii')
    for i in range(len(byte2)):
        byte2[i] ^= byte1[i % len(byte1)]
    m = hashlib.md5()
    m.update(byte2)
    result = base64.b64encode(m.digest()).decode('ascii')
    result = result.replace('/', '_')
    result = result.replace('+', '-')
    return result


def make_url(songNet, dfsId):
    encId = encrypted_id(dfsId)
    mp3_url = "http://%s/%s/%s.mp3" % (songNet, encId, dfsId)
    return mp3_url


site_info = "163.com"
download = netease_download
download_playlist = playlist_not_supported('netease')
