import redis

def Connect():
    return redis.Redis("127.0.0.1", "6379")
        

def Add(r, name, value):
    r.sadd(name, value)

def Sismember(r, name, value):
    return r.sismember(name, value)

def main():
    pass 

if __name__ == "__main__":
    main()


