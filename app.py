from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import os
import requests
import json
from steam_API_ import Steam_API


# Heroku變動prot
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
token = os.environ['line_bot_api_key']
# line_bot_api = LineBotApi(os.environ['line_bot_api_key'])
line_bot_api = LineBotApi(token)
handler = WebhookHandler(os.environ['handler_key'])

# 裝飾器 機器人進入點"/"
@app.route("/", methods=['POST'])
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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


    user_message = event.message.text
    print(user_message)
    if user_message[:1] == '#':
        print(user_message)
        user_message_search = user_message.replace('#','')
        steam = Steam_API('us','US')
        base_search = steam.search_game(user_message_search,1)

        CarouselColumn_val = []
        text_value1 = ''

        for i,val in enumerate(base_search['data']['results']):
            if i <= 10:
                steam_price = steam.game_price(val['plain'])
                print(steam_price['data'])
                for val2 in steam_price['data']:

                    text_value1 = f"遊戲名稱:{val2['title']}\n現在價格:{val2['now_price']}\n歷史低價:{val2['history_price']}\n\n"


                text_value1 =f"查詢結果:\n{text_value1}"
                print('text_value1')
                CarouselColumn_val.append(
                    CarouselColumn(thumbnail_image_url=steam_price['image'],
                    title=val['title'],
                    text=text_value1,
                    actions=[URIAction(label='前往商店',uri=steam_price['buy_url'])])
                )

        buttons_template_message = TemplateSendMessage(
        alt_text='Steam尋找遊戲',
        imageSize= "contain",
        template=CarouselTemplate(columns=CarouselColumn_val[0:])
)          
            
        line_bot_api.reply_message(event.reply_token, buttons_template_message)   

    
          



     





app.run(host='0.0.0.0', port=port)