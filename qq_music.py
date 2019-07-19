from bs4 import BeautifulSoup
import requests
import time
import re
import pandas as pd
import utils
import json


class QQMusicCrawler(object):

    def __init__(self, date):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.encoding = utils.get_website_encoding('http://y.qq.com', self.headers)
        self.date = pd.to_datetime(date, fmt='')
        self.week = self.date.week

    def get_rank_info(self, url):
        res = requests.get(url, headers=self.headers)
        res.encoding = self.encoding  # 同样读取和写入的编码格式
        data = json.loads(res.text, encoding=res.encoding)
        return data

    def extract_rank_songs(self, rank_data):
        cur_counts = [song['cur_count'] for song in rank_data['songlist']]
        in_counts = [song['in_count'] for song in rank_data['songlist']]
        old_counts = [song['old_count'] for song in rank_data['songlist']]
        albumname = [song['data']['albumname'] for song in rank_data['songlist']]
        albumids = [song['data']['albumid'] for song in rank_data['songlist']]
        singernames = [[singer['name'] for singer in song['data']['singer']] for song in rank_data['songlist']]
        singermids = [[singer['mid'] for singer in song['data']['singer']] for song in rank_data['songlist']]
        songnames = [song['data']['songname'] for song in rank_data['songlist']]
        songmids = [song['data']['songmid'] for song in rank_data['songlist']]
        rank_pop_df = pd.DataFrame(data=[cur_counts, in_counts, old_counts,
                                           albumname, albumids,
                                           singernames, singermids,
                                           songnames, songmids],
                                 columns=['cur_counts', 'in_counts', 'old_counts',
                                          'albumname', 'albumids',
                                          'singernames', 'singermids',
                                          'songnames', 'songmids'])
        return rank_pop_df

    def get_rank_pop(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2019-07-18&topid=4&type=top&song_begin=0&song_num=100&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
        rank_pop_data = self.get_rank_info(url)
        rank_pop_df = self.extract_rank_songs(rank_pop_data)
        time.sleep(1)
        return rank_pop_df

    def get_rank_hot(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2019_28&topid=26&type=top&song_begin=0&song_num=300&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
        rank_hot_data = self.get_rank_info(url)
        rank_hot_df = self.extract_rank_songs(rank_hot_data)
        time.sleep(1)
        return rank_hot_df

    def get_rank_new(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date=2019-07-15&topid=4&type=top&song_begin=0&song_num=100&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
        rank_hot_data = self.get_rank_info(url)
        rank_hot_df = self.extract_rank_songs(rank_hot_data)
        time.sleep(1)
        return rank_hot_df

    def get_rank_singers(self):
        urls = ['https://www.kugou.com/yy/singer/index/{}-all-1.html'.format(str(i)) for i in range(1, 6)]
        single_list = []
        for url in urls:
            single_list += self.get_singer_list(url)
            time.sleep(1)
        singer_df = pd.DataFrame(data=single_list, columns=['name', 'href', 'id'])
        return singer_df

    def get_singer_info(self):
        # TODO: Song info is not available in web version.
        #  Have to use app to find the api for getting the number of followers.
        #  Cannot login to the app using overseas IP.
        #  Will need to get others' help on that.
        pass

    def get_song_info(self):
        # TODO: Same as singer info.
        pass


if __name__ == '__main__':
    qmc = QQMusicCrawler('2019-7-18')
    qmc.get_rank_pop()
