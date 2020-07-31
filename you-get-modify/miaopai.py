#!/usr/bin/env python

__all__ = ['miaopai_download']

import string
import random
from ..common import *
import urllib.error
import urllib.parse
from ..util import fs

fake_headers_mobile = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
}

cookie='SINAGLOBAL=2230065238887.2153.1576732261719; UOR=,,login.sina.com.cn; un=13585869811; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WW-OwSBFUunLkKOoT2CV2GW5JpX5KMhUgL.Fo2cSozESKMRS0M2dJLoIp8pUcHEUs809s9rwryoUJiawBtt; ALF=1627611773; SSOLoginState=1596075775; SCF=ArcX_4qdMPE8iRy-Vugoqp0mYxLdnXOnnGBhC9Soarfifj7dEjWvNH0WBEWWNTMlL6VMg6TFSwNxc11nJBiYgLA.; SUB=_2A25yJl9QDeRhGedI7VAT9SnEzDuIHXVRUjeYrDV8PUNbmtANLXLQkW9NVu17v2C_dr1tS3zFQtyTa8sKEfmWeEdg; SUHB=079S9S5HM57ts3; YF-V5-G0=125128c5d7f9f51f96971f11468b5a3f; _s_tentry=login.sina.com.cn; Apache=6508176655471.183.1596075803764; wb_view_log_1662257877=1536*8641.25; ULV=1596075804734:63:16:4:6508176655471.183.1596075803764:1596003887217; YF-Page-G0=d30fd7265234f674761ebc75febc3a9f|1596078201|1596077976; YF-V-WEIBO-G0=35846f552801987f8c1e8f7cec0e2230; XSRF-TOKEN=y3T0oN-At_C_OgzCO3sA00TA; WBPSESS=idDIN7H4N-WNy0TN07peZrkEiPsivFa4J_3p6YtoN_9P4cwepLiiVmLWjU7b-z1CiweZSumhXLZ_Y7e2VnSH0uHLSt1ayLxbSG5cakM6bCSYQ5HxItTz6WrM7VDX5_5s; webim_unReadCount=%7B%22time%22%3A1596078488009%2C%22dm_pub_total%22%3A16%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A2%7D'


def weibo_headers(referer=None, cookie=None):
    # a reasonable UA
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'accept - language': 'zh - CN, zh;q = 0.9',
               'accept': 'application / json, text / plain, * / *',
               'accept - encoding': 'gzip, deflate, br',
               'origin': 'https://weibo.com',
               'User-Agent': ua}
    if referer is not None:
        headers.update({'Referer': referer})
    if cookie is not None:
        headers.update({'Cookie': cookie})
    return headers

def miaopai_download_by_fid(fid, output_dir = '.', merge = False, info_only = False, **kwargs):
    '''Source: Android mobile'''
    page_url = 'http://video.weibo.com/show?fid=' + fid + '&type=mp4'

    mobile_page = get_content(page_url, headers=fake_headers_mobile)
    url = match1(mobile_page, r'<video id=.*?src=[\'"](.*?)[\'"]\W')
    if url is None:
        wb_mp = re.search(r'<script src=([\'"])(.+?wb_mp\.js)\1>', mobile_page).group(2)
        return miaopai_download_by_wbmp(wb_mp, fid, output_dir=output_dir, merge=merge,
                                        info_only=info_only, total_size=None, **kwargs)
    title = match1(mobile_page, r'<title>((.|\n)+?)</title>')
    if not title:
        title = fid
    title = title.replace('\n', '_')
    ext, size = 'mp4', url_info(url)[2]
    print_info(site_info, title, ext, size)
    if not info_only:
        download_urls([url], title, ext, total_size=None, output_dir=output_dir, merge=merge)


def miaopai_download_by_wbmp(wbmp_url, fid, info_only=False, **kwargs):
    headers = {}
    headers.update(fake_headers_mobile)
    headers['Host'] = 'imgaliyuncdn.miaopai.com'
    wbmp = get_content(wbmp_url, headers=headers)
    appid = re.search(r'appid:\s*?([^,]+?),', wbmp).group(1)
    jsonp = re.search(r'jsonp:\s*?([\'"])(\w+?)\1', wbmp).group(2)
    population = [i for i in string.ascii_lowercase] + [i for i in string.digits]
    info_url = '{}?{}'.format('http://p.weibo.com/aj_media/info', parse.urlencode({
        'appid': appid.strip(),
        'fid': fid,
        jsonp.strip(): '_jsonp' + ''.join(random.sample(population, 11))
    }))
    headers['Host'] = 'p.weibo.com'
    jsonp_text = get_content(info_url, headers=headers)
    jsonp_dict = json.loads(match1(jsonp_text, r'\(({.+})\)'))
    if jsonp_dict['code'] != 200:
        log.wtf('[Failed] "%s"' % jsonp_dict['msg'])
    video_url = jsonp_dict['data']['meta_data'][0]['play_urls']['l']
    title = jsonp_dict['data']['description']
    title = title.replace('\n', '_')
    ext = 'mp4'
    headers['Host'] = 'f.us.sinaimg.cn'
    print_info(site_info, title, ext, url_info(video_url, headers=headers)[2])
    if not info_only:
        download_urls([video_url], fs.legitimize(title), ext, headers=headers, **kwargs)


def miaopai_download_story(url, output_dir='.', merge=False, info_only=False, **kwargs):
    data_url = 'https://m.weibo.cn/s/video/object?%s' % url.split('?')[1]
    data_content = get_content(data_url, headers=fake_headers_mobile)
    data = json.loads(data_content)
    title = data['data']['object']['summary']
    stream_url = data['data']['object']['stream']['url']

    ext = 'mp4'
    print_info(site_info, title, ext, url_info(stream_url, headers=fake_headers_mobile)[2])
    if not info_only:
        download_urls([stream_url], fs.legitimize(title), ext, total_size=None, headers=fake_headers_mobile, **kwargs)


def miaopai_download_direct(url, output_dir='.', merge=False, info_only=False, **kwargs):
    if 'tv/show' in url:
        """
        https://weibo.com/tv/show/1034:4531662764310554
        https://weibo.com/tv/api/component?page=%2Ftv%2Fshow%2F1034%3A4531662764310554&
        data={"Component_Play_Playinfo":{"oid":"1034:4531662764310554"}}
        """
        m = re.match(r'https?://weibo.com/tv/show/(\S+)', url)
        vid = m.group(1)
        data = vid + '&data={"Component_Play_Playinfo":{"oid":"%s"}}' % vid
        weibo_tv_api_url = 'https://weibo.com/tv/api/component?page=%2Ftv%2Fshow%2F' + data
        # cookie 必须要有否则会无法访问网页内容
        api_content = get_content(weibo_tv_api_url, headers=weibo_headers(cookie=cookie, referer=url))
        videos_info = json.loads(api_content)
        videos_info = videos_info['data']['Component_Play_Playinfo']
        if '1080p' in videos_info['urls']:
            title = videos_info['title'] + '-1080p'
            stream_url = 'http:' + videos_info['urls']['1080p']
        elif '720p' in videos_info['urls']:
            title = videos_info['title'] + '-720p'
            stream_url = 'http:' + videos_info['urls']['720p']
        elif '480p' in videos_info['urls']:
            title = videos_info['title'] + '-480p'
            stream_url = 'http:' + videos_info['urls']['480p']
        elif '360p' in videos_info['urls']:
            title = videos_info['title'] + '-360p'
            stream_url = 'http:' + videos_info['urls']['360p']
        else:
            raise Exception('Have no video url to download')
        size = url_size(stream_url, headers=weibo_headers(referer=stream_url))
        ext = 'mp4'
        print_info(site_info, title, ext, size)
        if not info_only:
            download_urls([stream_url], title, ext, size, output_dir=output_dir, merge=merge)
    else:
        mobile_page = get_content(url, headers=fake_headers_mobile)
        try:
            title = re.search(r'([\'"])title\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
        except:
            title = re.search(r'([\'"])status_title\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
        title = title.replace('\n', '_')
        try:
            stream_url = re.search(r'([\'"])stream_url\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
        except:
            page_url = re.search(r'([\'"])page_url\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
            return miaopai_download_story(page_url, info_only=info_only, output_dir=output_dir, merge=merge, **kwargs)

        ext = 'mp4'
        print_info(site_info, title, ext, url_info(stream_url, headers=fake_headers_mobile)[2])
        if not info_only:
            download_urls([stream_url], fs.legitimize(title), ext, total_size=None, headers=fake_headers_mobile, **kwargs)


def miaopai_download(url, output_dir='.', merge=False, info_only=False, **kwargs):
    if re.match(r'^http[s]://.*\.weibo\.com/\d+/.+', url):
        return miaopai_download_direct(url, info_only=info_only, output_dir=output_dir, merge=merge, **kwargs)

    if re.match(r'^http[s]://.*\.weibo\.(com|cn)/s/video/.+', url):
        return miaopai_download_story(url, info_only=info_only, output_dir=output_dir, merge=merge, **kwargs)

    # FIXME!
    if re.match(r'^http[s]://.*\.weibo\.com/tv/v/(\w+)', url):
        return miaopai_download_direct(url, info_only=info_only, output_dir=output_dir, merge=merge, **kwargs)

    if re.match(r'^http[s]://weibo\.com/tv/show/(\S+)', url):
        return miaopai_download_direct(url, info_only=info_only, output_dir=output_dir, merge=merge, **kwargs)

    fid = match1(url, r'\?fid=(\d{4}:\w+)')
    if fid is not None:
        miaopai_download_by_fid(fid, output_dir, merge, info_only)
    elif '/p/230444' in url:
        fid = match1(url, r'/p/230444(\w+)')
        miaopai_download_by_fid('1034:'+fid, output_dir, merge, info_only)
    else:
        mobile_page = get_content(url, headers = fake_headers_mobile)
        hit = re.search(r'"page_url"\s*:\s*"([^"]+)"', mobile_page)
        if not hit:
            raise Exception('Unknown pattern')
        else:
            escaped_url = hit.group(1)
            miaopai_download(urllib.parse.unquote(escaped_url), output_dir=output_dir, merge=merge, info_only=info_only, **kwargs)


site_info = "miaopai"
download = miaopai_download
download_playlist = playlist_not_supported('miaopai')
