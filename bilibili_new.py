import json
import jsonpath

from you_get.extractors import (
    imgur,
    magisto,
    youtube,
    missevan,
    acfun,
    netease,
    bilibili
)


def test_bilibil(url):
    """
    info_only：True=查看info信息不进行下载，False=视频下载，此时output_dir/merge是必备参数，否则报错
    output_dir:视频导出的路径
    merge：True=合并视频，False=不合并视频
    json_output：True=info以json格式输出，不会进行下载操作，False=普通格式输出，会执行下载操作
    caption：info_only=False时才有效；True=下载额外的信息，比如：subtitles, lyrics, danmaku，False=不下载
    :return:
    """
    bilibili.download_playlist(
        url, info_only=False, output_dir='D:\\bilibili_video', merge=True,
        json_output=False, caption=True
    )
    # bilibili.download(
    #     url, info_only=False, output_dir='D:\\bilibili_video', merge=True,
    #     json_output=False, caption=True
    # )


def test_netease(url):
    netease.download(
        url, info_only=False, output_dir='D:\\bilibili_video', merge=True,
        json_output=False, caption=True
    )


if __name__ == '__main__':
    # result_new = []
    # with open('D:\\bilibili_video\\result.json', 'r', encoding='utf-8') as f_obj:
    #     datas = json.load(f_obj)
    # print(len(datas))
    # for data in datas:
    #     if ' vs ' in data['title']:
    #         result_new.append(data)
    #         # url = 'https://www.bilibili.com/video/%s' % data['bvid']
    #         # test_bilibil(url)
    # print(len(result_new))
    # with open('D:\\bilibili_video\\result-new.json', 'w', encoding='utf-8') as f_obj:
    #     json.dump(result_new, f_obj, ensure_ascii=False, indent=4)

    # # 获取所有title的值
    # a = jsonpath.jsonpath(result_new, '$..bvid')
    # b = jsonpath.jsonpath(result_new, '$..title')

    # print(a)
    # print(b)
    test_netease('https://music.163.com/#/playlist?id=2819914042')
