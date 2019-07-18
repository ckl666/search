import socket
import sys
import Pack
import gevent
import time
import Redis
from gevent import monkey
monkey.patch_all()

"""
字节数#文件描述符#打包的格式#包的内容

master
solve将即将需要爬取的网页发送给master,
master收到url之后，取出已经爬取的,将剩余的分发给solve

多线程，一个线程负责查询

一个线程负责插入

"""
r = Redis.Connect()
# web服务器的链接
conn_web = set()
# 存储子服务器的链接
conn_solve = set()
flag_resoult = dict()

def createSockte():
    serverSocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port1 = 6666
    serverSocket1.bind((host,port1))
    serverSocket1.listen(5)

    port2 = 6667
    serverSocket2.bind((host,port2))
    serverSocket2.listen(5)
    
    return serverSocket1, serverSocket2

class combine:
    def __init__(self, conn):
        self.conn = conn
        self.urls_score = dict()
        self.solve_conns = list()
    # 所有查询都完成返回true 否则返回false
    def com(self, solve_conn, urls, weight):
        for i in range(len(urls)):
            if urls[i] in self.urls_score:
                self.urls_score[urls[i]] += weight[i]
            else:
                self.urls_score[urls[i]] = weight[i]
        self.solve_conns.append(solve_conn)
        for conn in conn_solve:
            if conn not in self.solve_conns:
                return False
        return True
    
    def sortUrl(self):
        tmp = sorted(self.urls_score.items(), key = lambda item:item[1], reverse = True)
        tmp = dict(tmp)
        return list(tmp.keys())

    def getConn(self):
        return self.conn


# 创建两个套接字，一个用于前端的查找，一个用于爬虫服务器的插入
def acceptConn(sock):
    while True:
        conn, addr = sock.accept()
        print("new connect %s" %(conn))
        if sock == serverSocket1:
            conn_web.add(conn)
            gevent.spawn(dealWebRequest, conn)
        else:
            conn_solve.add(conn)
            gevent.spawn(dealSolveRequest, conn)

# 从web读取数据
def readData(conn):
    len_pack = conn.recv(10).decode("gb2312")
    if len(len_pack) == 0:
        return None
    len_pack = int(len_pack.split("#")[0])
    li = list()
    while len_pack != 0:
        data = conn.recv(len_pack)
        if len(data) != 0:
            li.append(data)
            len_pack -= len(data)
        else:
            return None
    resoult = bytes()
    for l in li:
        resoult += l
    return resoult.decode("gb2312")

# 文件描述符#查询的关键语句
def dealWebRequest(conn):
    while True:
        resoult = readData(conn)
        if resoult is None:
            conn_web.remove(conn)
            conn.close()
            return None
        resoult = str(hash(conn)) + "#" + resoult
        print(resoult)
        str_len = str(len(resoult.encode("gb2312")))
        while len(str_len) < 10:
            str_len += "#"
        send_str = str_len + resoult
        print(send_str)
        for c in conn_solve:
            c.send(send_str.encode("gb2312"))    
        # 用于标记web服务器的请求
        conn_info = combine(conn)
        flag_resoult[hash(conn)] = conn_info
        # 查询结果
    

# 处理插叙返回的结果
def dealSolveRequest(conn):
    while True:
        # 如果链接断开的话就删除一个文件描述符
        resoult = readData(conn)
        if resoult is None:
            conn_solve.remove(conn)
            conn.close()
            return None
        resoult = resoult.split("#")
        # 接收solve的url检查重复的数据
        if resoult[1] == 's':
            urls = Pack.unpackUrl(resoult[0], resoult[2].encode("gb2312"))
            dealSolveResoult(urls)
        else:
            urls, weight = Pack.unpackUrlAndWeight(resoult[0], resoult[2].encode("gb2312"))
            print(urls)
            print(weight)
            conn_info =flag_resoult[int(resoult[1])]
            # 如果所有的节点都已经回复查询的结果，则直接给web端回复
            if conn_info.com(conn, urls, weight):
                writeWeb(conn_info)

# 处理url是否重复
def dealSolveResoult(urls):
    # 查询是否重复
    non_urls = []
    for url in urls:
        if not Redis.Sismember(r, url, 1):
            non_urls.append(url)
            Redis.Add(r, url, 1)

    count = len(conn_solve)
    gap = (len(non_urls) // count) + 1
    i = 0
    for conn in conn_solve:
        res_pack, res_pro = Pack.packUrl(non_urls[i:i+gap])
        i += gap
        send_str = res_pro + "#"
        len_str = str(len(send_str) + len(res_pack))
        while len(len_str) < 10:
            len_str += "#"
        send_str = len_str + send_str
        conn.send(send_str.encode("gb2312"))
        conn.send(res_pack)
    

# 向web发送数据
def writeWeb(conn_info):    
    conn = conn_info.getConn()
    urls = conn_info.sortUrl()
    res_pack,res_pro = Pack.packUrl(urls)
    send_str = res_pro + "#"
    len_str = str(len(send_str) + len(res_pack))
    while len(len_str) < 10:
        len_str += "#"
    send_str = len_str + send_str
    conn.send(send_str.encode("gb2312"))
    conn.send(res_pack)

serverSocket1, serverSocket2 = createSockte()
def main():
    while True:
        g1 = gevent.spawn(acceptConn, serverSocket1)
        g2 = gevent.spawn(acceptConn, serverSocket2)
        # gevent.sleep(1)
        g1.join()
        g2.join()

if __name__ == "__main__":
    main()
