from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('VO1hF5C+a2puZpEkPC/4anKPrJaKC3SBIMHrIp3FFEnm6gZATqTiIxMZurXAbPULJhwu/1/GL8J4ZeCsKMUpiKASUGO6Q4QAjHFnzhU7aXm4mfKwaQKix/gzA6W6ACFOFR3LyEpRZPz7qC0SrANZKAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('6cda3c995afd1d2713057a61e8ff0884')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    url = 'https://www.ptt.cc/bbs/cat/index.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    getRents = soup.findAll('div', 'r-ent')
    i = 0
    urlList = [0]
    data = ''
    for getRent in getRents:
        i += 1
        meta = getRent.find('div', 'title').find('a')
        if meta:
            getTitle = meta.text.strip()                      #取得標題
            getHref = meta.get('href')                        #取得網址
            getDate = getRent.find('div', 'date').text        #取得日期
            getAuthor = getRent.find('div', 'author').text    #取得作者
            urlList.append('https://www.ptt.cc' + getHref)    #將網址存入清單
            data = data + ('{0:0>2}. {1:5} {2:<15}\n{3}\n'.format(i, getDate, getAuthor, getTitle))
        else:
            getDate = getRent.find('div', 'date').text
            urlList.append(' ')
            data = data+('{0:0>2}. {1:5}\n{2:>23}\n'.format(i, getDate, '(本文已被刪除)'))

    if event.message.text=='0':
        reply = data
    else:
        x = int(event.message.text)
        if x>i or x<0:
            reply = '無此編號請重新輸入\n或輸入0顯示標題清單'
        else:
            new_url = urlList[x]
            detail = ''
            if new_url==' ':
                reply = '本文已被刪除'
            else:
                new_response = requests.get(new_url)    #取得所選文章之HTML
                new_soup = BeautifulSoup(new_response.text, 'html.parser')
                getScreens = new_soup.findAll('div', 'bbs-screen bbs-content')
                for getScreen in getScreens:
                    detail = detail + getScreen.text
            reply = detail
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
