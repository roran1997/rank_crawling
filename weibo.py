import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from utils import scroll_page, scroll_to_page_end
import pandas as pd

class WeiboCrawler(object):

    def get_user_main_page(self):
        url = 'https://m.weibo.cn/p/1005051624923463'
        pass

    def get_rank_super_topic(self):
        url = 'https://huati.weibo.cn/discovery/super?extparam=ctg1_2%7Cscorll_1&luicode=10000011&lfid=100803_-_super#'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome(executable_path='driver/chromedriver', options=options)
        driver.get(url)
        for i in range(5):
            temp_elems = driver.find_elements_by_css_selector('div.card-list')
            driver.execute_script("arguments[0].scrollIntoView();", temp_elems[-1])
            time.sleep(1)

        elems = driver.find_elements_by_css_selector('div.card-list')
        rank_st_list = []
        for elem in elems[:100]:
            text = ''
            for a in elem.text:
                text += a
            text_list = text.split('\n')
            try:
                a = text_list[2].split()
                topic_info = dict(
                    rank = text_list[0][3:],
                    name = text_list[1],
                    infn = text_list[2].split()[0][:-3],
                    fans = text_list[2].split()[1][:-2])
                rank_st_list.append(topic_info)
            except:
                print(rank_st_list[-1])
                print(text_list)
        rank_st_df = pd.DataFrame(rank_st_list)
        return rank_st_df

date = pd.to_datetime('today').strftime('%Y-%m-%d')
wc = WeiboCrawler()
ran_st = wc.get_rank_super_topic()
ran_st.to_csv('super_topic_{}.csv'.format(date), index=False)
