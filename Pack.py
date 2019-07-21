import struct


def packUrl(urls):
    res_pro = ""
    for url in urls:
        url_len = len(url.encode("gb2312"))
        res_pro += str(url_len) + "s"
    args = []
    for url in urls:
        args.append(url.encode("gb2312"))

    return struct.pack(res_pro, *args), res_pro

def unpackUrl(res_pro, res_pack):
    res = struct.unpack(res_pro, res_pack)
    urls = []
    for url in res:
        urls.append(url.decode("gb2312"))
    return urls

# 文件描述符与url_weight
def packUrlAndWeight(urls_score):
    res_pro = ""
    for url_score in urls_score:
        url_len = len(url_score[0].encode("gb2312"))
        res_pro += str(url_len) + "s"
        weight_len = len(str(url_score[1]))
        res_pro += str(weight_len) + "s"

    args = []
    for url_score in urls_score:
        args.append(url_score[0].encode("gb2312"))
        args.append(str(url_score[1]).encode("gb2312"))

    return struct.pack(res_pro, *args), res_pro

def unpackUrlAndWeight(res_pro, res_pack):
    res = struct.unpack(res_pro, res_pack)
    len_res = len(res)
    urls = []
    weight = []
    for i in range(len_res):
        if i%2 == 0:
            urls.append(res[i].decode("gb2312"))
        else:
            weight.append(float(res[i]))
    return urls, weight
    

def main():
    pass

if __name__ == "__main__":
    main()

