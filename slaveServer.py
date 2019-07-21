import socket
import jieba
import Pack
import search
import MySQL
import spider
import threading

def createSocket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 6667
    s.connect((host, port))
    return s

# 从master服务器读取数据
def readData(db1, db2, conn):
    len_pack = conn.recv(10).decode("gb2312")
    if len(len_pack) == 0:
        conn.close()
    len_pack = int(len_pack.split("#")[0])
    li = list()
    while len_pack != 0:
        data = conn.recv(len_pack)
        if len(data) != 0:
            li.append(data)
            len_pack -= len(data)
        else:
            conn.close()
    resoult = bytes()
    for l in li:
        resoult += l
    resoult = resoult.decode("gb2312").split("#")
    if len(resoult) == 2 and resoult[1][:4] == "http":
        db = MySQL.connectDatabase()
        t = threading.Thread(target = dealSpiderRequest, args = (db, conn, resoult))
        t.start()
        # dealSpiderRequest(db, conn, resoult)
        # 处理爬虫
    elif len(resoult) == 2:
        t = threading.Thread(target = dealWebRequest, args = (db2, conn, resoult))
        t.start()
        # dealWebRequest(db, conn, resoult)
        # 处理查询


def dealWebRequest(db, conn, resoult):
    words = jieba.cut(resoult[1])
    urls_score = search.sortUrl(db, words)
    res_pack,res_pro = Pack.packUrlAndWeight(urls_score)
    send_str = res_pro + "#" + resoult[0] + "#"
    len_str = str(len(send_str) + len(res_pack))
    while len(len_str) < 10:
        len_str += "#"
    send_str = len_str + send_str
    # print(send_str)
    conn.send(send_str.encode("gb2312"))
    if len(res_pack) != 0: 
        conn.send(res_pack)

def dealSpiderRequest(db, conn, resoult):
    urls = Pack.unpackUrl(resoult[0], resoult[1].encode("gb2312"))
    # 爬取master 发送过来的网页,
    urls = list(spider.iterSpider(db, urls, 1))
    if len(urls) == 0:
        return None
    # 将爬到的url发送给master 服务器 
    res_pack, res_pro = Pack.packUrl(urls)
     
    send_str = res_pro + "#" + "s" + "#"
    len_str = str(len(send_str) + len(res_pack))
    while len(len_str) < 10:
        len_str += "#"
    
    send_str = len_str + send_str
    conn.send(send_str.encode("gb2312"))
    conn.send(res_pack)
    MySQL.disconnect(db)
    print(send_str)
    print(res_pack)


def searchData(db, words):
    return search.sortUrl(db, words)
     

def main():
    db1 = MySQL.connectDatabase()
    db2 = MySQL.connectDatabase()
    s = createSocket()
    urls = ["https://www.163.com"]
    res_pack, res_pro = Pack.packUrl(urls)
    resoult = list()
    resoult.append(res_pro)
    resoult.append(res_pack.decode("gb2312"))
    dealSpiderRequest(db1, s, resoult)
    while True:
        readData(db1, db2, s)


if __name__ == "__main__":
    main()
