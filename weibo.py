import time
from selenium import webdriver
import pandas as pd
import os
from utils import launch_driver_in_headless_mode


class WeiboCrawler(object):

    def __init__(self):
        self.driver = launch_driver_in_headless_mode()
        self.dt = pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')


    def get_user_num_fans(self, id):
        url = 'https://m.weibo.cn/p/{}'.format(id)
        self.driver.get(url)
        time.sleep(3)
        nk_name = self.driver.find_element_by_css_selector('span.txt-shadow').text
        elems = self.driver.find_elements_by_css_selector('div.txt-shadow')
        num_fans = int(elems[1].text[2:])
        return nk_name, num_fans

    def extract_hcy_num_fans_to_csv(self):
        nk_name, num_fans = self.get_user_num_fans('1005051624923463')
        hcy_fans = pd.DataFrame({'nick_name': [nk_name], 'num_fans': [num_fans], 'datetime': self.dt})
        hcy_fans_cvs_file = 'weibo_results/hcy_fans.csv'
        if os.path.exists(hcy_fans_cvs_file):
            hcy_past_fans = pd.read_csv(hcy_fans_cvs_file)
            hcy_fans = hcy_past_fans.append(hcy_fans)
        hcy_fans.to_csv(hcy_fans_cvs_file, index=False)
        return 'Number of fans of {}: {} has been saved to csv files. '.format(nk_name, num_fans)

    def get_rank_super_topic(self):
        url = 'https://huati.weibo.cn/discovery/super?extparam=ctg1_2%7Cscorll_1&luicode=10000011&lfid=100803_-_super#'
        self.driver.get(url)
        num_elems = 0
        while num_elems < 101:
            print('Number of super topic presented: {}, scroll down.'.format(num_elems))
            elems = self.driver.find_elements_by_css_selector('div.card-list')
            self.driver.execute_script("arguments[0].scrollIntoView();", elems[-1])
            num_elems = len(elems)
            time.sleep(5)
        rank_st_list = []

        for elem in elems[:100]:
            text = ''
            for a in elem.text:
                text += a
            text_list = text.split('\n')
            topic_info = dict(
                rank = text_list[0][3:],
                name = text_list[1],
                infn = text_list[2].split()[0][:-3],
                fans = text_list[2].split()[1][:-2],
                time = self.dt)
            rank_st_list.append(topic_info)
        rank_st_df = pd.DataFrame(rank_st_list)
        self.driver.quit()
        return rank_st_df

    def extract_super_topic_data_to_csv(self):
        cur_st = self.get_rank_super_topic()
        super_topic_cvs_file = 'weibo_results/super_topic.csv'
        if os.path.exists(super_topic_cvs_file):
            past_st = pd.read_csv(super_topic_cvs_file)
            cur_st = past_st.append(cur_st)
        cur_st.to_csv(super_topic_cvs_file, index=False)

    def quit_driver(self):
        self.driver.quit()


wc = WeiboCrawler()
wc.extract_hcy_num_fans_to_csv()
wc.extract_super_topic_data_to_csv()
wc.quit_driver()



