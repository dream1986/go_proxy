#!/usr/bin/python3
#-*- coding: utf-8 -*-
#encoding=utf-8

import time
import sys
import os
import re
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse
import urllib

from db import SearchDB

import cgi

print('Content-type:text/html; charset=utf-8')
print()

GOOGLE_URL = "https://www.google.com/search" 
#GOOGLE_URL = "https://www.google.com/search?q=%s" 
GOOGLE_HEAD = {"Host":"www.google.com",
              "Referer":"https://www.google.com/",
              "Connection":"keep-alive",
              "Accept-Encoding":"deflate",
              "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0",
              }

    
htmls_head = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN" xml:lang="zh-CN">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<head>
<title>Anyshare, Search What You Want!</title>
</head>
<body>
"""

htmls_style = """
<style type="text/css"> 
<!-- 
.g_content_items {   
    font-family: tahoma, 'microsoft yahei', 微软雅黑;
}

em {
    color: red
}
--> 
</style> 
"""

htmls_search_e = """
<form action="/search.py" method="GET" align=left>
    <span style="font-size:17px"><a href="./index.htm">回到首页</a></span>
    <input type='text' name='q' value='%s' style="background-color:#EEEEEE;height:20px;width:300px;font-size:17px"/>
    <input type='submit' name='Search' value='搜一下' style="background-color:#EEEEEE;height:23px;width:70px;font-size:18px"/>
</form>
"""


htmls_body2 = """
    <span>搜索字段为空，请不要骗我...</span>
"""


htmls_end = """    
</body>
</html>
"""


search_params = cgi.FieldStorage()
search_keywords = search_params.getvalue("q")
search_start = search_params.getvalue("start", default="0")
search_q = urllib.parse.urlencode({'q':search_keywords, 'start': search_start})  

google_q = GOOGLE_URL + '?' + search_q

#如果搜索字段为空
if not search_keywords:
    print(htmls_head)
    print(htmls_search)
    print(htmls_body2)
    print(htmls_end)
    os.exit(0)

htmls_search = htmls_search_e % search_keywords

try:
    request = urllib.request.Request(google_q, headers = GOOGLE_HEAD)
    g_response = urllib.request.urlopen(request)
    g_read = g_response.read()
except Exception as e:
    print ("异常:"+str(e))
    
    
if 'HTTP_X_FORWARDED_FOR' in os.environ.keys():
    ip = os.environ['HTTP_X_FORWARDED_FOR']
elif 'REMOTE_ADDR' in os.environ.keys():
    ip = os.environ['REMOTE_ADDR']
else:  
    ip = ""
    
soup = BeautifulSoup(g_read)
stats = soup.find('div', attrs={"id":"resultStats"})
g_group = soup.find('div', attrs={"class":"srg"})
g_items = g_group.findAll('li', attrs={"class":"g"})
navs = soup.find('table', attrs={"id":"nav"})

if ip:
    htmls_body1 = """
	<span>欢迎使用[%s]，搜索关键词：%s，搜索状态：%s</span>
    """ % (ip, search_keywords, stats.text)
else:
    htmls_body1 = """
	<span>欢迎使用，搜索关键词：%s，搜索状态：%s</span>
    """ % (search_keywords, stats.text)

db = SearchDB()
db.db_insert_search(ip, search_keywords)
#db.db_dump()
#db.db_statistics()


print(htmls_head)
print(htmls_style)
print(htmls_search)
print(htmls_body1)
print ('<h4>搜索结果:</h4>')


#for item, item_desc in zip(items, items_desc):
for g_item in g_items:
    if g_item:
        item = g_item.find('h3', attrs={"class":"r"})
        item_desc = g_item.find('span', attrs={"class":"st"})
        item_caches = g_item.findAll('li', attrs={"class":"action-menu-item ab_dropdownitem"})
        print ( '<div class="g_content_items">' )
        print ( '<span style="font-size:16px"><a href=' + item.a["href"] + '>' + item.a.text + '</a></span>')
        print ( '<br />' )
        print ( '<span>' + item.a['href']+ '</span>')
        print ( '<br />' )
        print ( '<span> <a style="font-size:16px" target="_blank" href="https://192.3.90.124/cache.py?url=' + item.a["href"] + '"> 页面快照&nbsp;</a></span>')
        if item_caches:
            for i_cache in item_caches:
                # Here, because we can not access http://webcache.googleusercontent.com/ until
                # we crack there anti-robot ...
                if i_cache:
                    if not re.match(r'^(http|https)://',i_cache.a["href"]) and re.match(r'^/search?',i_cache.a["href"]):
                        print ('<span><a style="font-size:16px" href=' + repr(i_cache.a["href"])+'>' + '&nbsp;类似结果&nbsp;' + '</a></span>')
        print ( '<br />' )
        print ( item_desc )
        print ( '<br />' )
        print ( '<br />' )
        print ( '</div>' )
    
if navs:
    tabs = navs.findAll('td')
    if tabs:
        print('<table><tr>')
        for tab in tabs:
            if tab:
                print(tab)
        print('</table></tr>')
        
print(htmls_end)

