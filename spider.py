import urllib
from bs4 import BeautifulSoup
import sys
import re
import jieba
import jieba.analyse
import os
import MySQL


ignorewords = ["，", "、", "。", "的", "你", "我", "他"]

# 爬取网页
def getSoup(url):
    try:
        c = urllib.request.urlopen(url)
    except:
        print("Could not open %s" %(url))
        return None
    html = c.read()
    soup = BeautifulSoup(html, "lxml")
    # print(soup)
    return soup

# 获取网页中的超链接
def getUrl(db, soup, page):
    links = soup('a')
    urls = set()
    # words = []
    for link in links:
        if 'href' in dict(link.attrs):
            url = urllib.parse.urljoin(page, link['href'])
            url = url.split('<')[0]
            url = url.split('#')[0]
            if url[:4] != 'http':
                continue
            urls.add(url)
            link = str(link)
            index_i = 0
            index_j = 0
            for i in range(len(link)):
                if link[i] == '>':
                    index_i = i+1
                if index_i != 0 and link[i] == '<':
                    index_j = i
                    break
            # words.append(link[index_i:index_j])
            res = splitWord(link[index_i:index_j])
            createLinkWordIndex(db, res, url)
            # print(link[index_i:index_j])
    return urls

# 获取网页的文本
def getText(soup):
    [script.extract() for script in soup.findAll('script')]
    [style.extract() for style in soup.findAll('style')]

    reg = re.compile("<[^>]*>")
    content = reg.sub('', soup.prettify()).strip()
    content = " ".join(content.split())

    # print(content)
    return content

def splitLinkWord(text):
    seg_list = jieba.cut_for_search(text)
    res = []
    for seg in seg_list:
        if seg[0] in ignorewords:
            continue
        else:
            res.append(seg)
    return res

# 分割词语
def splitWord(content):
    seg_list = jieba.analyse.textrank(content, topK = 20, withWeight = True, allowPOS = ("ns", "n", "vn", "v"))
    res = []
    for seg in seg_list:
        if seg[0] in ignorewords:
            continue
        else:
            res.append(seg)
    return res

# 迭代爬取网页  将网页中的url收集返回
def iterSpider(db, url_list, n):
    next_urls = set()
    for url in url_list:
        next_urls.add(url)
    for i in range(n):
        urls = next_urls.copy()
        next_urls.clear()
        for url in urls:
            # 解析网页的htmp格式
            soup = getSoup(url)
            if soup is None:
                continue
            # 获取网页中的文本
            text = getText(soup)
            print("====")
            # 将网页中的此进行分割 统计出高频词汇建立索引
            res = splitWord(text)
            createIndex(db, res, url)
            # 获取网页的超链接再次爬取
            tmp_set = getUrl(db, soup, url)
            next_urls = next_urls.union(tmp_set)
            createLinkIndex(db, url, next_urls)
            tmp_set.clear()
        print(next_urls)
    return next_urls


# 设置多线程
# 建立索引
def createIndex(db, words, url):
    # 向wordlist中添加值
    urlid = getUrlId(db, url)
    for word in words:
        wordid = getWordId(db, word)
        sql = "select urlid from wordlocation where wordid = " + str(wordid) + " and urlid = " + str(urlid) + ";"
        res = MySQL.query(db, sql)
        if len(res) == 0:
            MySQL.insertValues(db, "wordlocation",["wordid", "urlid", "weight"],[[str(wordid), str(urlid), str(word[1])]])

def getUrlId(db, url):
    print(type(url))
    sql = "select id from urllist where url = " + "'" + url + "';"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        url = "'" + url + "'"
        if len(url) > 200:
            return None
        MySQL.insertValues(db, "urllist", ["url"], [[url]])
        res = MySQL.query(db, sql)
    return res[0][0]


def getWordId(db, word):
    sql = "select id from wordlist where word = " + "'" + word[0] + "';"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        # 将元素插入到wordlist中
        str_word = "'" + word[0] + "'"
        MySQL.insertValues(db, "wordlist", ["word"],[[str_word]])
        res = MySQL.query(db,sql)
    return res[0][0]


def createLinkWordIndex(db, words, url):
    if len(words) == 0:
        return 
    urlid = getUrlId(db, url)
    for word in words:
        str_word = "'" + word[0] + "'"
        sql = "select linkid from linkword where word = " + str_word + ";"
        res_urlid = MySQL.query(db, sql)
        if res_urlid is None:
            MySQL.insertValues(db, "linkword", ["word", "linkid"], [[str_word, str(urlid)]])
        else:
            for urlid_query in res_urlid:
                if urlid_query[0] ==  urlid:
                    break
            else:
                MySQL.insertValues(db, "linkword", ["word", "linkid"], [[str_word, str(urlid)]])
                

def createLinkIndex(db, url, urls):
    fromid = getUrlId(db, url)
    if fromid is None:
        return None
    for link in urls:
        toid = getUrlId(db, link)
        MySQL.insertValues(db, "link", ["fromid", "toid"], [[str(fromid), str(toid)]])

def main():
    db = MySQL.connectDatabase()
    
    MySQL.createTable(db)

    # iterSpider(db, ["http://www.csdn.net"], 3)
    
    
    # MySQL.insertValues(db, "urllist", ["url", "qwe"], [["'qwe'","'ppp'"]])
    '''
    soup = test()
    getUrl(soup)
    text = getTest(soup)
    res = splitWord(text)
    '''
    # print("/".join(res))

if __name__ == "__main__":
    main()

