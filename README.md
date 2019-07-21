# search
运行：
- 首先手动创建一个search数据库(数据库的名字可以随意),在MySQL.py中修改需要链接的数据库的名字即可
- 运行python3 MySQL.py 创建数据表与索引
    
- 然后python3 masterServer.py运行主服务器(需要安转redis, gevent库)
    
- 接着python3 slaveServer.py运行从节点，负责存储,该节点上运行着爬虫程序，为了减少网络的传输，降低编程的难度，将爬虫程序直接运行在存储节点上，对数据直接可以写入数据库中(需要安转jieba库)

- 非网页版的执行 python3 webServer.py 在masterServer的终端看到有新的链接建立，之后在webServer所在的终端输入查询的内容即可
- 如果想要运行网页版的进入flask_test目录，执行 python3 first_flask.py runserver 然后在浏览器输入(127.0.0.1:5000)即可访问
    （网页版的需要安转flask框架）
    
- 支持多个slave节点,如果想要运行多个slaveServer在一台机器上，
- 需要新建一个数据库,修改MySQL.py中的链接的数据库，再执行一次python3 MySQL.py创建表，slaveServer.py中首次爬取的网页链接建议修改一下，不然两个数据库中
    都存储了第一次爬取的链接，当爬取结束之后会向master服务器发送当前页面的所有超链接，master在这些超链接中挑选出没有被爬过的链接分发给所有的子服务器
    如果不修改话，由于上一个slave服务器已经发送过这些超链接，所以当前的slave短时间内得不到爬取页面的任务，但是不会影响查询
