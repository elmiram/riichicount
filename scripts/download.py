﻿# coding=utf-8
"""
Скачать иконки с тайлами с сайта клуба тэсудзи.

Этот скрипт был написан отдельно на третьем питоне, а приложение на фласке писалось на втором.
Но я решила вставить сюда этот скрипт тоже, для полноты картины и просто на всякий случай.
"""

import urllib.request
import re

url = 'http://tesuji-club.ru/wp-content/plugins/wp-monalisa/icons/'


def get_links():

    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    links = re.findall('<a href="(.*?)">', text)[1:]
    return links


imgs = get_links()
for i in imgs:
    urllib.request.urlretrieve(url + i, 'static/img/' + i)


