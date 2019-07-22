from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import utils
import json
import random
from selenium import webdriver


def is_given_date_equals_today(date):
    return pd.to_datetime(date, format='%Y-%m-%d').date() == pd.to_datetime('today').date()


def is_given_week_equals_todays_week(date):
    return is_week_of_the_given_date_equals_todays_week_start_at_thursday(date) & \
           (pd.to_datetime(date, format='%Y-%m-%d') > pd.to_datetime('today') - pd.Timedelta('1W'))


def is_week_of_the_given_date_equals_todays_week_start_at_thursday(date):
    date = pd.to_datetime(date, format='%Y-%m-%d')
    if pd.to_datetime('today').dayofweek <= 2:
        return date.week == pd.to_datetime('today').week - 1
    else:
        return date.week == pd.to_datetime('today').week


def is_given_date_before_thursday(date):
    date = pd.to_datetime(date, format='%Y-%m-%d')
    return True if date.dayofweek <= 2 else False


def roll_back_datetime(dt, td):
    return pd.to_datetime(dt) - pd.Timedelta(td)


def get_number_of_week_to_roll_back(date):
    num_rweek = 0
    if is_given_week_equals_todays_week(date):
        num_rweek += 1
    if is_given_date_before_thursday(date):
        num_rweek += 1
    return num_rweek


class QQMusicCrawler(object):

    def __init__(self, date):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.encoding = utils.get_website_encoding('http://y.qq.com', self.headers)
        if is_given_date_equals_today(date):
            self.date = roll_back_datetime(date, '1D').strftime('%Y-%m-%d')
        else:
            self.date = pd.to_datetime(date).strftime('%Y-%m-%d')

        date_for_week = pd.to_datetime(roll_back_datetime(date, '{}W'.format(get_number_of_week_to_roll_back(date))))
        self.week = '{}_{}'.format(date_for_week.year, date_for_week.week)
        print('Querying ranking for date: {}, week: {}'.format(self.date, self.week))

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

    def get_rank_info(self, url):
        res = requests.get(url, headers=self.headers)
        res.encoding = self.encoding
        data = json.loads(res.text, encoding=res.encoding)
        data = self.extract_rank_songs(data)
        return data

    def get_rank_pop(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date={}' \
              '&topid=4&type=top&song_begin=%7B%7D'.format(self.date)
        rank_pop_df = self.get_rank_info(url)
        time.sleep(1)
        return rank_pop_df

    def get_rank_hot(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date={}' \
              '&topid=26&type=top&song_begin=%7B%7D'.format(self.week)
        rank_hot_df = self.get_rank_info(url)
        time.sleep(1)
        return rank_hot_df

    def get_rank_new(self):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?tpl=3&page=detail&date={}' \
              '&topid=27&type=top&song_begin=%7B%7D'.format(self.date)
        rank_new_df = self.get_rank_info(url)
        time.sleep(1)
        return rank_new_df

    def get_area_singer_mid(self, area_code):
        singer_mid_list = []
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(executable_path='driver/chromedriver', chrome_options=options)
        urls = ['https://y.qq.com/portal/singer_list.html#area={}&page={}&'.format(area_code, i) for i in range(1, 4)]
        for url in urls:
            driver.get(url)
            time.sleep(7)  # seconds
            soup = BeautifulSoup(driver.page_source, 'lxml')
            singer_mid_list += list(set([singer.get('data-singermid') for singer in soup.find_all('a', 'singer_list__cover')]))
            singer_mid_list += list(set([singer.get('data-singermid') for singer in soup.find_all('a', 'singer_list_txt__link')]))
            time.sleep(random.random() + 0.5)
        driver.quit()
        return singer_mid_list

    def get_singer_info(self, mid):
        url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getUCGI9862812093915763&g_tk=5381&loginUin=0&hostUin=0' \
              '&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0' \
              '&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A0%7D%2C%22singer%22%3A%7B%22method%22%3A%22' \
              'get_singer_detail_info%22%2C%22param%22%3A%7B%22sort%22%3A5%2C%22singermid%22%3A%22{}%22%2C%22sin%22' \
              '%3A0%2C%22num%22%3A10%7D%2C%22module%22%3A%22music.web_singer_info_svr%22%7D%7D'.format(mid)
        res = requests.get(url, headers=self.headers)
        res.encoding = self.encoding
        data = json.loads(res.text, encoding=res.encoding)
        singer_info = self.extract_singer_info(data)
        return singer_info

    def extract_singer_info(self, data):
        data =  data['singer']['data']
        singer_info = dict(
            mid = data['singer_info']['mid'],
            name = data['singer_info']['name'],
            fans = data['singer_info']['fans'],
            total_album = data['total_album'],
            total_mv = data['total_mv'],
            total_song = data['total_song'])
        return singer_info

    def get_singer_list(self):
        mainland_area_code = '200'
        hk_tw_area_code = '2'
        singer_list = []
        singer_mid_list = self.get_area_singer_mid(mainland_area_code) + self.get_area_singer_mid(hk_tw_area_code)
        for mid in singer_mid_list[:10]:
            singer_list.append(self.get_singer_info(mid))
            time.sleep(random.random() + 0.5)
        singer_df = pd.DataFrame(singer_list)
        return singer_df

    def get_song_info(self, mid):
        url = 'https://c.y.qq.com/node/m/client/cmt_list/index.html?type=1&id={}'.format(mid)
        res = requests.get(url, headers=self.headers)
        res.encoding = self.encoding
        soup = BeautifulSoup(res.text, 'lxml')
        song_info = dict(
            mid = mid,
            title = soup.find('h2', 'comment_song__tit').text.strip(),
            num_comments = soup.find_all('span', 'comment__number')[2].text)
        return song_info


if __name__ == '__main__':
    qmc = QQMusicCrawler('2019-7-20')
    song_info = qmc.get_song_info('213374282')
    singer_info = qmc.get_singer_info('002Vcz8F2hpBQj')
    rank_pop = qmc.get_rank_pop()
    rank_hot = qmc.get_rank_hot()
    rank_new = qmc.get_rank_new()
    singer_df = qmc.get_singer_list()
    singer_df.to_csv('test_qq_singer_list.csv', index=False)



