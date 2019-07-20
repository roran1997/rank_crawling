from bs4 import BeautifulSoup
import requests
import time
import re
import pandas as pd
import utils
import json


def is_given_date_equals_today(date):
    return pd.to_datetime(date, format='%Y-%m-%d').date() == pd.to_datetime('today').date()


def is_given_week_equals_todays_week(date):
    print(pd.to_datetime(date, format='%Y-%m-%d').week )
    print(pd.to_datetime('today').week)
    return (pd.to_datetime(date, format='%Y-%m-%d').week == pd.to_datetime('today').week) & \
           (pd.to_datetime(date, format='%Y-%m-%d') > pd.to_datetime('today') - pd.Timedelta('1W'))


def roll_back_datetime(dt, td):
    return pd.to_datetime(dt) - pd.Timedelta(td)


class QQMusicCrawler(object):

    def __init__(self, date):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.encoding = utils.get_website_encoding('http://y.qq.com', self.headers)
        if is_given_date_equals_today(date):
            self.date = roll_back_datetime(date, '1D').strftime('%Y-%m-%d')
        else:
            self.date = date
        # if is_given_week_equals_todays_week(date):
        #     print(roll_back_datetime(date, '1W'))
        #     print(roll_back_datetime(date, '1W').week)
        #     self.week = roll_back_datetime(date, '1W').strftime('%Y-%w')
        # else:
        self.week = pd.to_datetime(date, format='%Y-%m-%d').strftime('%Y_%W')

    def get_rank_info(self, url):
        res = requests.get(url, headers=self.headers)
        res.encoding = self.encoding  # 同样读取和写入的编码格式
        data = json.loads(res.text, encoding=res.encoding)
        return data

    def extract_rank_songs(self, rank_data):
        def get_rank_first_lvl_value(key):
            value_list = [song[key] for song in rank_data['songlist']]
            return value_list

        def get_rank_second_lvl_data_value(key):
            value_list = [song['data'][key] for song in rank_data['songlist']]
            return value_list

        def get_rank_second_lvl_singer_value(key):
            value_list = [[singer[key] for singer in song['data']['singer']] for song in rank_data['songlist']]
            return value_list

        cur_counts = get_rank_first_lvl_value('cur_count')
        in_counts = get_rank_first_lvl_value('in_count')
        old_counts = get_rank_first_lvl_value('old_count')
        albumnames = get_rank_second_lvl_data_value('albumname')
        albummids = get_rank_second_lvl_data_value('albummid')
        songnames = get_rank_second_lvl_data_value('songname')
        songmids = get_rank_second_lvl_data_value('songmid')
        singernames = get_rank_second_lvl_singer_value('name')
        singermids = get_rank_second_lvl_singer_value('mid')

        rank_df = pd.DataFrame({
            'cur_count': cur_counts,
            'in_count': in_counts,
            'old_count': old_counts,
            'albumname': albumnames,
            'albummid': albummids,
            'singername': singernames,
            'singermid': singermids,
            'songname': songnames,
            'songmid': songmids
        })
        return rank_df

    def get_rank_pop(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&' \
              'page=detail&date={}&topid=4&type=top&song_begin=0&song_num=100' \
              '&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json' \
              '&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(self.date)
        rank_pop_data = self.get_rank_info(url)
        rank_pop_df = self.extract_rank_songs(rank_pop_data)
        time.sleep(1)
        return rank_pop_df

    def get_rank_hot(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date={}&topid=26&type=top' \
              '&song_begin=0&song_num=300&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json&inCharset=utf8' \
              '&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(self.week)
        print(url)

        rank_hot_data = self.get_rank_info(url)
        rank_hot_df = self.extract_rank_songs(rank_hot_data)
        time.sleep(1)
        return rank_hot_df

    def get_rank_new(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&' \
              'page=detail&date={}&topid=4&type=top&song_begin=0&song_num=100' \
              '&g_tk=1597243877&loginUin=1278077260&hostUin=0&format=json&inCharset=utf8' \
              '&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'.format(self.date)
        rank_new_data = self.get_rank_info(url)
        rank_new_df = self.extract_rank_songs(rank_new_data)
        time.sleep(1)
        return rank_new_df

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
    qmc = QQMusicCrawler('2019-7-20')
    qmc.get_rank_pop()
    qmc.get_rank_hot()
    qmc.get_rank_new()
