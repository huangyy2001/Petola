import os
from flask import Flask
app = Flask(__name__)

from flask import request, abort,render_template
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent, TextSendMessage,TemplateSendMessage, ConfirmTemplate, MessageTemplateAction, ButtonsTemplate,PostbackTemplateAction, URITemplateAction, CarouselTemplate, CarouselColumn,ImageCarouselTemplate, ImageCarouselColumn, ImageSendMessage
from urllib.parse import parse_qsl

line_bot_api = LineBotApi('FpUQ9LoxdKrSIGbKq8aRdaN9ZGKqO0AgzSIU3pbmSvzfCrrI0yLgjOnZiM6CsyQzCX9YN4BYsAfDJUwPL9SOINqs6jCKSNWzuewyAnDB1G4Yq6yxN/7lhJw/2vi6FVR5lNbJxmOn24i9e2XWHPXdFAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('44d298103c9d1eda3e3b617f381f65ae')

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
    PRIMARY KEY (id));
    
    CREATE TABLE peteat (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    feederweight character varying(50) NOT NULL,
    feedertime character varying(50) NOT NULL,
    PRIMARY KEY (id));
    
    CREATE TABLE petlive (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    urllink VARCHAR(255) NOT NULL,
    PRIMARY KEY (id));

    CREATE TABLE login (
    id serial Not NULL,
    uid character varying(50) NOT NULL,
    petolacode character varying(50) NOT NULL,
    petolapassword VARCHAR(50) NOT NULL,
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
        return render_template('AF_form.html', liffid = '2000165683-DnZvQJY9')

@app.route('/page2')
def page2():
        return render_template('login.html', liffid = '2000165683-ZRnNwJaQ')	


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
               thumbnail_image_url='https://i.imgur.com/1NSDAvo.jpg',
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
     message = TextSendMessage(
     text = '現在溫度及濕度為:'
     )
     line_bot_api.reply_message(event.reply_token, message)
 except:
     line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))



def manageForm_login(event, mtext, user_id):
    try:
        flist = mtext[3:].split('/')
        petolacode = flist[0]  #取得輸入資料
        petolapassword = flist[1]
        sql_cmd = "insert into login (uid, petolacode, petolapassword) values('" + user_id + "', '" + petolacode + "', '" + petolapassword +"');"
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
       
        message = TextSendMessage(  #顯示訂房資料
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))     

        
if __name__ == '__main__':
 app.run()
 
 