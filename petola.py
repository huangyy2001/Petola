import os
from flask import Flask
app = Flask(__name__)

from flask import request, abort,render_template
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage,TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, ButtonsTemplate,PostbackTemplateAction, URITemplateAction, CarouselTemplate, CarouselColumn,ImageCarouselTemplate, ImageCarouselColumn, ImageSendMessage
from urllib.parse import parse_qsl

line_bot_api = LineBotApi('8ry4aG0vf0yOCHde9WaBIXYTUQnWQOqMnzXq6UZm1EvbRC7YAuFpj723ob7XqCR03WWpbeWqk0RzsCwwr61/Tzd8DDOKv1F9uBrmfWm6YHe+YiCPHXqbk5SNHLUGeuHK7ViYyfvL9a46l6Q5Z4eTXgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f1d2d07660f86c3b81def0bb5c6dbff1')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://admin:123456@127.0.0.1:5432/petola'
db = SQLAlchemy(app)

# 重置資料庫
@app.route('/createdb')
def createdb():
    sql = """
    DROP TABLE IF EXISTS pethouse, peteat, petlive,login ,users;

    CREATE TABLE pethouse (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    fan BOOLEAN,
    timestamp TIMESTAMP,
    PRIMARY KEY (id));
    
    CREATE TABLE peteat (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    feederweight character varying(50) NOT NULL,
    feedertime TIMESTAMP,
    PRIMARY KEY (id));
    
    CREATE TABLE petlive (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    urllink character varying(50) NOT NULL,
    PRIMARY KEY (id));
    
    CREATE TABLE login (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    user_name character varying(50) NOT NULL,
    user_password character varying(50) NOT NULL,
    PRIMARY KEY (id));
    
    CREATE TABLE users(
    id serial Not NULL, 
    uid character varying(50) NOT NULL,
    PRIMARY KEY (id));
    """
    
    db.engine.execute(sql)    
    return "資料表建立成功！"



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route('/page1')
def page1():
        return render_template('AF_form.html', liffid = '1661380630-Dkpr3bxe')

@app.route('/page2')
def page2():
        return render_template('login.html', liffid = '1661380630-WD6VZap1')	


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):   
    user_id = event.source.user_id
    sql_cmd = "select * from users where uid='" + user_id + "'"
    query_data = db.engine.execute(sql_cmd)
    if len(list(query_data)) == 0:
        sql_cmd = "insert into users (uid) values('" + user_id + "');"
        db.engine.execute(sql_cmd)
        
    mtext = event.message.text
    if mtext == '@產品登入':
        sendLogin(event)
    elif mtext == '@自動餵食器':
         sendAF(event)
    elif mtext == '@即時影像':
         sendlive(event)
    elif mtext == '@艙內環境':
         sendHE(event)
    elif mtext[:3] == '!!!' and len(mtext) > 3:
         manageForm_login(event, mtext, user_id)         
    elif mtext[:3] == '###' and len(mtext) > 3:
         manageForm_AF(event, mtext, user_id)
  
         
def sendLogin(event, user_id): #使用者登入
     try:
         sql_cmd = "select * from login where uid='" + user_id + "'"
         query_data = db.engine.execute(sql_cmd)
         if len(list(query_data)) == 0:
             message = TemplateSendMessage(
                 alt_text='自動餵食器',
                 template = ButtonsTemplate(
                     thumbnail_image_url='https://i.imgur.com/1NSDAvo.jpg',
                     title='產品登入',
                     text='登入後即可使用功能',
                     actions=[
                     URITemplateAction(label='使用者登入', uri='https://liff.line.me/' + '1661380630-WD6VZap1')  
                 ]
             )
         )
         line_bot_api.reply_message(event.reply_token,message)
        
     except:
         line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
     
def sendAF(event,user_id): #自動餵食器
   try:
       sql_cmd = "select * from login where uid='" + user_id + "'"
       query_data = db.engine.execute(sql_cmd)
       message = TemplateSendMessage(
       alt_text='自動餵食器',
       template = ButtonsTemplate(
               thumbnail_image_url='https://imgur.com/o5v8WUv.png',
               title='自動餵食器',
               text='登入後即可使用功能',
               actions=[
                   URITemplateAction(label='自動餵食器', uri='https://liff.line.me/' + '1661380630-Dkpr3bxe')
               ]
           )
       )
       line_bot_api.reply_message(event.reply_token,message)
   except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendlive(event): #即時影像
    try:
        message = TemplateSendMessage(
        alt_text='即時影像',
        template=ButtonsTemplate(
        thumbnail_image_url='https://i.imgur.com/qaAdBkR.png', #顯示的圖片
        title='即時影像', #主標題
        text='請選擇：', #副標題
        actions=[
        URITemplateAction( #開啟網頁
        label='即時影像',
        uri='https://www.shu.edu.tw/'
        ),
        ]
        )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def sendHE(event):
    try:
        # 查询pethouse表中的数据
        pethouse_query = db.session.execute("SELECT * FROM pethouse ORDER BY id DESC LIMIT 1").fetchone()

        # 查询peteat表中的数据
        peteat_query = db.session.execute("SELECT * FROM peteat").fetchall()

        # 创建消息文本
        message_text = "目前艙內：\n"
        if pethouse_query:
           fan_status = "開" if pethouse_query['fan'] else "關"
           message_text += f"溫度: {pethouse_query['temperature']}度, 濕度: {pethouse_query['humidity']}%, 風扇狀態: {fan_status}\n"

        message_text += "\n目前餵食排程：\n"
        for row in peteat_query:
            message_text += f"餵食時間: {row['feedertime']}, 餵食量: {row['feederweight']}g\n"

        message = TextSendMessage(text=message_text)
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

def manageForm_login(event, mtext, user_id):
    try:
        flist = mtext[3:].split('/')
        petolacode = flist[0]  #取得輸入資料
        petolapassword = flist[1]
        sql_cmd = "insert into login (uid, user_name, user_password) values('" + user_id + "', '" + petolacode + "', '" + petolapassword +"');"
        db.engine.execute(sql_cmd)        
        text1 = '登入成功' 

        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

  
def manageForm_AF(event, mtext, user_id):
    try:
        flist = mtext[3:].split('/')
        feedingType = flist[0]
        feedingTime = flist[1]  #取得輸入資料
        feedingAmount = flist[2]
        sql_cmd = "insert into peteat (uid, feederweight, feedertime) values('" + user_id + "', '" + feedingAmount + "', '" + feedingTime +"');"
        db.engine.execute(sql_cmd)
        text1 = "您的餵食排程已成功，資料如下："
        text1 += "\n餵食方式：" + feedingType
        text1 += "\n餵食時間：" + feedingTime
        text1 += "\n餵食量：" + feedingAmount
       
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))     

        
if __name__ == '__main__':
 app.run()
 
 