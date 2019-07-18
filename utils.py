import re
import requests


def get_website_encoding(url, headers):  # 一般每个网站自己的网页编码都是一致的,所以只需要搜索一次主页确定
    res = requests.get(url, headers=headers)
    charset = re.search("charset=(.*?)>", res.text)
    if charset is not None:
        blocked = ['\'', ' ', '\"', '/']
        filter = [c for c in charset.group(1) if c not in blocked]
        return ''.join(filter)  # 修改res编码格式为源网页的格式,防止出现乱码
    else:
        return res.encoding  # 没有找到编码格式,返回res的默认编码

