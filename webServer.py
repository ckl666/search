import socket
import Pack

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 6666
    s.connect((host, port))
    return s
    
def readData(conn):
    len_pack = conn.recv(10).decode("gb2312")
    len_pack = int(len_pack.split("#")[0])
    li = list()
    while len_pack != 0:
        data = conn.recv(len_pack)
        if len(data) <= len_pack:
            li.append(data)
            len_pack -= len(data)
    resoult = bytes()
    for l in li:
        resoult += l
    resoult = resoult.decode("gb2312").split("#")
    resoult = Pack.unpackUrl(resoult[0], resoult[1].encode("gb2312"))
    return resoult

def writeData(conn, sentence):
    len_str = str(len(sentence.encode("gb2312")))
    while len(len_str) < 10:
        len_str += "#"
    send_str = len_str + str(sentence)
    print(send_str)
    conn.send(send_str.encode("gb2312"))
    

def main():
    s = connect()
    while True:
        data = input()
        writeData(s, data)
        resoult = readData(s)
        for url in resoult:
            print(url)

if __name__ == "__main__":
    main()
