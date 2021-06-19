from flask import Flask, request, render_template,redirect,send_from_directory,jsonify
import json
from flask import Flask, render_template, session, flash, redirect, url_for, escape, request
from flask_bootstrap import Bootstrap
import sqlite3
import pandas as pd
import random
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import base64


users = {
    'james@example.com': {
        'name': 'James',
        'password': '1'
    },
    'frank@example.com': {
        'name': 'Frank',
        'password': '12345'
    }
}


def execute_db(fname, sql_cmd):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(sql_cmd)
    conn.commit()
    conn.close()


def execute_pandas(fname,table_name,col ,a):
    sql = "SELECT * FROM %s where %s = '%s'" % (table_name,col, a)
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    packs= pd.DataFrame(data = c.execute(sql))
    conn.commit()
    conn.close()
    return packs 


def select_db(fname, sql_cmd):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(sql_cmd)
    rows = c.fetchall()
    conn.close()
    return rows

db_name = 'db.sqlite'
db_name_account = 'account.sqlite'

def create_sql():
    try:
        
        print('建立資料庫及資料表')
        cmd = 'CREATE TABLE record (id INTEGER PRIMARY KEY AUTOINCREMENT, \
            pk_id,\
            name TEXT NOT NULL UNIQUE,\
            age ,\
            phone)'
        return execute_db(db_name, cmd)
    except:
        print('已創建相同名稱資料庫')


def create_account():
    try:
        
        print('建立資料庫及資料表')
        cmd = 'CREATE TABLE account (id INTEGER PRIMARY KEY AUTOINCREMENT, \
            email TEXT NOT NULL UNIQUE,\
            name ,\
            password)'
        return execute_db(db_name_account, cmd)
    except:
        print('已創建相同名稱資料庫')
create_sql()
create_account()



## ===================雖肌生成驗證碼===================
random_base="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def random_vc():
    vc_pieces=random.sample(random_base,4)
    return ''.join(vc_pieces)

def random_text_color():
    return (random.randint(127,255),random.randint(127,255),random.randint(127,255))

def random_bg_color():
    return (random.randint(32,127),random.randint(32,127),random.randint(32,127))

def word2pic(word):#根据验证码生成验证码图片
    image=Image.new('RGB',(100,30),random_bg_color())
    font=ImageFont.truetype('arial.ttf',15)
    draw=ImageDraw.Draw(image)
    for t in range(4):
        draw.text((25*t+10,5),word[t],font=font,fill=random_text_color())

    bytesIO=BytesIO()
    image.save(bytesIO,format='JPEG')

    return base64.b64encode(bytesIO.getvalue()).decode()

## ===================雖肌生成驗證碼===================



app = Flask(__name__)
app.secret_key = 'Foobarj823!42vs#46Jd_d3_Zaylk@'
Bootstrap(app)


@app.route('/get_vc')
def get_vc():
    vc=random_vc()#生成随机验证码
    session['comment_vc']=vc#写入session
    vc_image=word2pic(vc)#生成验证码图片数据
    return 'data:image/jpeg;base64,'+vc_image#返回图片数据



## login還沒有讀取db
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('index'))

    if request.method == 'POST':

        pd_login = execute_pandas(db_name_account,'account','email',request.form['inputemail'])

        if len(pd_login)==1:

            if request.form['inputpassword'] == list(pd_login[3])[0] :
                session['username'] = request.form['inputemail']
                if request.form['verificationCode'].lower()==session.get('comment_vc').lower():
                    print("成功")
                    flash('You have successfully logged in')
                    return redirect(url_for('success'))
                else:
                    print("失敗")
                    flash('驗證碼錯誤')
                    # return redirect(url_for('login'))

            else:
                flash('Incorrect Password', 'bad')
                return redirect(url_for('login'))
        else:
            flash('{} not registered'.format(request.form['inputemail']), 'bad')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():


    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        a = request.form['inputemail']
        
        packs = execute_pandas(db_name_account,'account','email', a)

        # if request.form['inputemail'] not in users:
        if len(packs) == 0:
            username = request.form['inputemail']
            name = request.form['inputname']
            password = request.form['inputpassword']
            users[username] = {}
            users[username]['name'] = name
            users[username]['password'] = password


            cmd = 'INSERT INTO account \
            (   email,\
                name ,\
                password) VALUES \
            ("%s", "%s", "%s")'% \
            (
            username,
            name,
            password,
            )
            # print("到這裡")
            execute_db(db_name_account, cmd) 


            # values = cursor.execute(cmd)

            flash('User has been registered')
            return redirect(url_for('login'))

        # if request.form['inputemail'] in users:
        if len(packs) == 1:
            flash('User already registered', 'bad')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    
    session.pop('username', None)
    flash('You have been sucessfully logged out', 'ok')
    return redirect(url_for('success'))


@app.route('/success')
def success():
    
    if 'username' in session:
        username = execute_pandas(db_name_account,'account','email',session['username'])
        # return render_template('index.html', username=users[session['username']]['name'])
        return render_template('index.html', username= list(username[2])[0] )
    return render_template('login.html')


@app.route('/data_input')
def data_input():
    if 'username' in session:
        username = execute_pandas(db_name_account,'account','email',session['username'])
        return render_template('data_input.html', username= list(username[2])[0] )
    return render_template('login.html')


@app.route("/sql", methods=['GET', 'POST'])
def json_msgT():
    if request.method == "POST":
        username = execute_pandas(db_name_account,'account','email',session['username'])
        name = request.form["name"]
        MATCH = json.loads(name)
        print(MATCH)
        cmd = 'INSERT INTO record \
            (   pk_id,\
                name,\
                age ,\
                phone) VALUES \
            ("%s","%s", "%s", "%s")'% \
            (
            list(username[0])[0],
            MATCH["name"],
            MATCH["age"],
            MATCH["phone"],
            )
        execute_db(db_name, cmd) 
        result = jsonify(
            button =  " 您已儲存成功"   
        )
        return result


## 還沒有匯入pandas到前端
@app.route("/data_pandas")
def data_pandas():
    if 'username' in session:
        username = execute_pandas(db_name_account,'account','email',session['username'])
        session_pk_id = list(username[0])[0]
        pd_df = execute_pandas(db_name,'record','pk_id',session_pk_id)
        if len(pd_df) >0:
            pd_df.columns = ['id','pk_id','name','age','phone']
            ID = pd_df.iloc[-1]["id"]
            name = pd_df.iloc[-1]["name"]
            age = pd_df.iloc[-1]["age"]
            phone = pd_df.iloc[-1]["phone"]
            # return render_template('data_pandas.html',username= list(username[2])[0], tables=[pd_df.to_html(classes='data')], titles=pd_df.columns.values)
            return render_template('data_pandas.html',ID=ID , name=name , age=age , phone=phone)
        else:
            return render_template('data_pandas_nan.html',username= list(username[2])[0])
    return render_template('login.html')


@app.route("/")
def index_home():
    return render_template("home.html")


@app.route("/images/<filename>")
def uploaded_file(filename):
    return send_from_directory('images',filename)


@app.route("/images/favicons/<filename>")
def webmanifest (filename):
    return send_from_directory('images/favicons',filename)


@app.route("/data/<filename>")
def emgu (filename):
    return send_from_directory('static',filename)

if __name__ == "__main__":
    app.run()