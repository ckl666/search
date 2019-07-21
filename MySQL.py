import pymysql 
import sys

def connectDatabase(addr = "localhost", user = "root", passwd = "1234...", database = "search"):
    try:
        db = pymysql.connect(addr, user, passwd, database)
    except:
        print("database connect error")
        sys.exit()
    return db

def createTable(db):
    createUrllist = "create table urllist(id int(10) primary key auto_increment, url varchar(500));"
    alterUrllist = "alter table urllist change url url varchar(500) character set utf8 not null;"
    createWordlist = "create table wordlist(id int(20) primary key auto_increment, word varchar(50));"
    alterWordlist = "alter table wordlist change word word varchar(100) character set utf8 not null;"
    createWordlocation = "create table wordlocation(urlid int(10),wordid int(20), weight double);"
    createLink = "create table link(fromid int(10), toid int(10))"
    createLinkWord = "create table linkword(word varchar(50),linkid int(10))"
    alterWordLink = "alter table linkword change word word varchar(100) character set utf8 not null;"
    createUrlIndex = "create index url_index on urllist(url);"
    createWordIndex = "create index word_index on wordlist(word);"
    createLocationIndex = "create index wordid_index on wordlocation(wordid);"
    createLinkIndex = "create index link_index on link(toid);"
    createLinkWordIndex = "create index linkword_index on linkword(word);"
    try:
        cursor = db.cursor()
        cursor.execute(createUrllist)
        cursor.execute(alterUrllist)
        cursor.execute(createWordlist)
        cursor.execute(alterWordlist)
        cursor.execute(createWordlocation)
        cursor.execute(createLink)
        cursor.execute(createLinkWord)
        cursor.execute(alterWordLink)
        cursor.execute(createUrlIndex)
        cursor.execute(createWordIndex)
        cursor.execute(createLocationIndex)
        cursor.execute(createLinkIndex)
        cursor.execute(createLinkWordIndex)
        db.commit()
    except:
        db.rollback()
        print("table create error")

def insertValues(db, table, keys, values):
    sql = "insert into " + table
    colu = ','.join(keys)
    colu = "(" + colu + ")"
    sql = sql + colu
    sql = sql + " values "
    for value in values:
        str_tmp =",".join(value)
        str_tmp = "(" + str_tmp + "),"
        sql = sql + str_tmp
    print (sql[0:-1])
    try:
        cursor = db.cursor()
        if len(sql) > 500:
            return None
        cursor.execute(sql[0:-1])
        db.commit()
    except:
        db.rollback()
        print("insert error")

def query(db, sql):
    cursor = db.cursor()
    try:
        cursor.execute(sql)
    except:
        print("query error %s" %(sql))
        sys.exit()
    return cursor.fetchall()

def disconnect(db):
    db.close()


        
def main():
    db = connectDatabase()
    createTable(db)

if __name__ == "__main__":
    main()
