import MySQL
import socket
import jieba.analyse
import spider

def sortUrl(db, words):
    url_score = dict()
    linkid_set = set()
    for word in words:
        wordid = getWordId(db, word)
        if wordid is None:
            continue
        urlid_weight = getUrlId(db, wordid)
        if urlid_weight is None:
            continue
# 计算权值的比分
        for url_info in urlid_weight:
            url =  getUrl(db, url_info[0])
            # 保存urlid 用于后面计算链接之间的分值
            if url is None:
                continue
            linkid_set.add((url_info[0],url))
            setUrlScore(url_score, url, url_info[1])
# 计算链接说明文字的比分 
        linkid_res = getLinkId(db, word)
        if linkid_res is None:
            continue
        else:
            for linkid in linkid_res:
                url = getUrl(db, linkid[0])
                if url is None:
                    continue
                else:
                    linkid_set.add((linkid[0],url))
                    setUrlScore(url_score, url, 0.5)
        # 根据链接之间的关系计算比分
    url_score = countLinkScore(db, url_score, linkid_set)
    # 根据url_score 的值进行排序
    url_score = sorted(url_score.items(), key = lambda item:item[1],reverse = True)
    for url in url_score:
        print("url:%s, weight:%s" %(url[0], url[1]))
    return url_score



# 根据链接之间的关系计算比分
def countLinkScore(db, url_score, linkid_set):
    # 存放url 对应的pr
    page_rank = dict()
    # 存放当前url链接向哪些url
    urlfrom_to = dict()
    # 存放当前url 来自那些url
    urlto_from = dict()
    # 初始化pr
    for linkid in linkid_set:
        page_rank[linkid[0]] = 1.0
        urlfrom_to[linkid[0]] = list()
        urlto_from[linkid[0]] = list()

    # 初始化当前链接指向的其他链接
    """
    for linkid in linkid_set:
        linktoid = getToUrlId(db, linkid)
        if linktoid is None:
            continue
        else:
            for tmp_id in linktoid:
                urlfrom_to[linkid[0]].append(tmp_id[0])
    """
        
    # 初始其他链接指向的当前链接
    for linkid in linkid_set:
        linkfromid = getFromUrlId(db, linkid[0])
        if linkfromid is None:
            continue
        else:
            for tmp_id in linkfromid:
                urlto_from[linkid[0]].append(tmp_id[0])

    iteratortion = 20
    for i in range(iteratortion):
        for linkid in linkid_set:
            linkid_list = urlto_from[linkid[0]]
            page_rank[linkid[0]] = len(linkid_list) * 0.85
    
    for linkid in linkid_set:
        setUrlScore(url_score, linkid[1], page_rank[linkid[0]])

    return url_score

def getToUrlId(db, urlid):
    sql = "select toid from link where fromid = " + str(urlid) + ";"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        return None
    else:
        return res

# 一个urlid 可能对应多个fromid
def getFromUrlId(db, urlid):
    sql = "select fromid from link where toid = " + str(urlid) + ";"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        return None
    else:
        return res

# 可能一个关键字对应多个linkid 
def getLinkId(db, word):
    sql = "select linkid from linkword where word = " + "'" + word + "';"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        return  None
    else:
        return res

def getWordId(db, word):
    sql = "select id from wordlist where word = " + "'" + word + "';"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        return None
    return res[0][0]

def getUrl(db,urlid):
    sql = "select url from urllist where id = " + str(urlid) + ";"
    res = MySQL.query(db, sql)
    if len(res) == 0:
        return None;
    return res[0][0]

# 返回关键字在页面中的权值和页面的id
def getUrlId(db, wordid):
    sql2 = "select urlid, weight from wordlocation where wordid = " + str(wordid) + ";"
    res = MySQL.query(db, sql2)
    if len(res) == 0:
        return None
    return res

# 传入一个字典url_score ,字符串url, double类型的score
def setUrlScore(url_score, url, score):
    if url in url_score:
        url_score[url] += score
    else:
        url_score[url] = score

def main():
    str_input = input("输入查询的内容:")
    db = MySQL.connectDatabase()
    print("你查询的关键字:%s" %(str_input))
    words = jieba.cut(str_input)
    sortUrl(db, words)

if __name__ == "__main__":
    main()

