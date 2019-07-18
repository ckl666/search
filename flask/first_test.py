from flask import Flask,render_template, request, redirect, url_for
from werkzeug.routing import BaseConverter
from flask_script import Manager
import pymysql
import webServer

conn = webServer.connect( )

# 打开数据库连接
# db = pymysql.connect("localhost", "root", "mysql", "searchengines")

#正则表达式转换器
class RegexConverter(BaseConverter):
    def __init__(self,url_map,*items):
        super(RegexConverter,self).__init__(url_map)
        self.regex=items[0]

app = Flask(__name__)
app.secret_key = 'itheima'
pymysql.install_as_MySQLdb( )
search = ""

# cursor = db.cursor()

# SQL 查询语句
"""
def sr(search):
    sql = "select url from urllist where id in(select urlid from wordlocation where wordid = (select id from wordlist where word like \'%"+search+"%\'));"
    sql.encode('utf-8')
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        return results
    except:
        print("Error: unable to fetch data")

    # 关闭数据库连接
"""

#将正则表达转换器设点到url_map中
app.url_map.converters['regex']=RegexConverter
manager = Manager(app)

@app.route('/',methods=['POST','GET'])
def judge():
    from forms import Search
    search_form = Search( )
    if request.method == 'POST':

        #判断参数
        if search_form.validate_on_submit( ):
            search = search_form.search.data
            print(search)
            #if search is not None:
            return redirect(url_for('.go', search=search))
    return render_template('search.html', title='Search', form=search_form)


            #服务器查询
          #  webServer.writeData(conn, search)
        #   result = webServer.readData(conn)





#返回结果页面
@app.route('/go',methods=['POST', 'GET'])
def go( ):
    # GET请求
    from forms import Search
    search_form = Search()
    # 判断参数
    if search_form.validate_on_submit():
        search = search_form.search.data
        webServer.writeData(conn, search)
        print(search)
        if request.method == "POST":
            # resqult = sr(search)
            resqult = webServer.readData(conn)
            values = [search,]
            for url in resqult:
                url = url.decode("gb2312")
                values.append(url)

            if len(values) > 1:
                return render_template("result.html", result=values, form1=search_form)
           # return render_template("result.html", title='Result', form1=search_form)
        else:
            pass
            #print("data:", search)
        values = []
        values.append("%s" % search)
        print(values)
        return render_template('result.html', result=values,form1 = search_form)

    #return redirect(url_for('.go', result=request.data))

#正则匹配路由
@app.route('/user/<regex("[a-z]{3}"):username>')
def user(username):
    return 'Username is %s' %username


@app.route('/<regex("(https?:?//([^/]*))(/.*)?"):url>')
def ll(url):
    return url


@manager.command
def dev():
    from livereload import Server
    live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')
    live_server.serve(open_url=True)


if __name__ == '__main__':
    manager.run( )
    #app.run(debug=True)
