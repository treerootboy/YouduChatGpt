# -*- coding: utf-8 -*-

"""
回调模式示例，简单企业应用示例
!!需要用python3.5+运行!!
"""


from aiohttp import web, ClientSession
from urllib.parse import parse_qsl

import entapp.client as app
from entapp.message import *
from entapp.aes import AESCrypto
from entapp.aes import generate_signature
from entapp.utils import *
import time
import os


"""
环境变量
"""
for key, value in os.environ.items():
    print(f"{key}={value}")

PORT = int(os.getenv('PORT')) or 8001
RECEIVE_MSG_API = os.getenv('RECEIVE_MSG_API') or '/msg/receive'

YOUDU_BUIN = int(os.getenv('YOUDU_BUIN'))
YOUDU_APP_ID = os.getenv('YOUDU_APP_ID')
YOUDU_AES_KEY = os.getenv('YOUDU_AES_KEY')
YOUDU_CALLBACK_TOKEN = os.getenv('YOUDU_CALLBACK_TOKEN') 
YOUDU_ADDRESS = os.getenv('YOUDU_ADDRESS') or '192.168.8.180:7080'
YOUDU_DOWNLOAD_DIR = os.getenv('YOUDU_DOWNLOAD_DIR') 

OPENAI_EMAIL = os.getenv('OPENAI_EMAIL')
OPENAI_PWD = os.getenv('OPENAI_PWD')
OPENAI_KEY = os.getenv('OPENAI_KEY')
OPENAI_ENGINE = os.getenv('OPENAI_ENGINE') or 'text-davinci-003'
THINKING_TEXT = os.getenv('THINKING_TEXT')
CHATGPT_PROXY = os.getenv('CHATGPT_PROXY')



"""
接收消息
"""
client = app.AppClient(YOUDU_BUIN, YOUDU_APP_ID, YOUDU_AES_KEY, YOUDU_ADDRESS)
async def receive_msg(req):
    query_dict = dict(parse_qsl(req.query_string))
    signature = query_dict.get('msg_signature')
    if not is_instance(signature, unicode_str(), str):
        print('msg_signature is invalid')
        return

    nonce = query_dict.get('nonce')
    if not is_instance(nonce, unicode_str(), str):
        print('nonce is invalid')
        return

    timestamp = query_dict.get('timestamp')
    if not is_instance(timestamp, unicode_str(), str):
        print('timestamp is invalid')
        return

    json_obj = None
    try:
        json_obj = await req.json()
    except ValueError as e:
        print('failed to decode json', e)
        return

    encrypt = json_obj.get('encrypt')
    if not is_instance(encrypt, unicode_str(), str):
        print('encrypt content is invalid')
        return

    my_signature = generate_signature(YOUDU_CALLBACK_TOKEN, timestamp, nonce, encrypt)
    if pystr(signature) != my_signature:
        print('signature not match')
        return

    to_buin = json_obj.get('toBuin')
    if not isinstance(to_buin, int):
        print('toBuin is invalid')
        return

    to_app = json_obj.get('toApp')
    if not is_instance(to_app, unicode_str(), str):
        print('toApp is invalid')
        return

    if to_buin != YOUDU_BUIN or to_app != YOUDU_APP_ID:
        print('buin or appId not match')
        return

    msg_dict = json_loads_utf8(pystr(AESCrypto(YOUDU_APP_ID, YOUDU_AES_KEY).decrypt(encrypt)))
    msg = ReceiveMessage().from_json_object(msg_dict)
    print(str(msg))

    if msg.msg_type == MESSAGE_TYPE_IMAGE:
        client.download_file(msg.msg_body.to_image_body().media_id, YOUDU_DOWNLOAD_DIR)
    elif msg.msg_type == MESSAGE_TYPE_FILE:
        client.download_file(msg.msg_body.to_file_body().media_id, YOUDU_DOWNLOAD_DIR)
    else:
        if msg.from_user and msg.create_time > time.time() - 15:
            if THINKING_TEXT:
                await chatgpt_thinking(msg)
            try:
                if OPENAI_ENGINE == 'chatgpt' :
                    await chatgpt_api(msg)
                else:
                    await openai_api(msg)
            except Exception as e:
                alert_user_error(msg, e)
                
def alert_user_error(msg, e):
    client.send_msg(Message(
        msg.from_user, 
        MESSAGE_TYPE_TEXT, 
        TextBody('''openai api 发生错误: 
%s''' %  e))
    )
            
            
"""
chatgpt 思考中的默认回应
"""
async def chatgpt_thinking(msg):
    client.send_msg(Message(
        msg.from_user, 
        MESSAGE_TYPE_TEXT, 
        TextBody('%s 思考中...' % OPENAI_ENGINE))
    )



"""
openai api 回复
"""
import openai
openai.api_key = OPENAI_KEY
async def openai_api(msg):
    openai.aiosession.set(ClientSession())
    completion = await openai.Completion.acreate(
        engine=OPENAI_ENGINE, 
        prompt=msg.msg_body.content, 
        max_tokens=3000)
    chatResponse = TextBody(str(completion.choices[0].text).lstrip())
    print(completion)
    client.send_msg(Message(msg.from_user, MESSAGE_TYPE_TEXT, chatResponse))
    await openai.aiosession.get().close()
    
class UserSession:
    def __init__(self, user):
        self.user = user
        self.conversation = []
        self.createtime = time.time()

    async def chat(self, text):
        print('会话[', self.user ,']询问:', text)
        self.conversation.append({
            'role':'user',
            'content':text
        })
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=self.conversation
        )
        print('gpt是否有返回？', completion is None)
        self.conversation.append(completion.choices[0].message)
        print('会话[', self.user ,']回答:', completion.choices[0].message.content)
        return completion.choices[0].message.content

    @classmethod
    def get(cls, user):
        return SessionCollection.getInstance().get(user)
        

class SessionCollection(dict):
    def __init__(self):
        super().__init__()
        
    def get(self, user, default=None):
        try:
            if user not in self \
            or time.time() - self[user].createtime > 86400:
                print('创建用户:', user)
                self[user] = UserSession(user)
                print('创建用户成功', user)
            
            return self[user]
        except Exception:
            pass
        
        return default

    @classmethod
    def getInstance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance
    


"""
chatgpt 回复
"""
async def chatgpt_api(msg):
    session = UserSession.get(msg.from_user)
    print(session)
    completion = await session.chat(msg.msg_body.content)
    client.send_msg(Message(
        msg.from_user, 
        MESSAGE_TYPE_TEXT, 
        TextBody(str(completion).lstrip()))
    )


"""
aiohttp web 服务
"""
from aiohttp.web import middleware
@middleware
async def errorHandler(request, handler):
    try:
        await handler(request)
    except Exception as e:
        print(e)
        pass
    return web.json_response({'errcode': 0, 'errmsg': 'ok', 'encrypt': None})

# 创建服务
def init_server():
    app = web.Application(middlewares=[errorHandler])
    app.router.add_post(RECEIVE_MSG_API, receive_msg)
    app.router.add_get(RECEIVE_MSG_API, receive_msg)
    return app


# 启动服务
web.run_app(init_server(), port=PORT)
