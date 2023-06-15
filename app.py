# -*- coding: utf-8 -*-
import traceback
from aiohttp import web, ClientSession
from urllib.parse import parse_qsl

import entapp.client as app
from entapp.message import *
from entapp.aes import AESCrypto
from entapp.aes import generate_signature
from entapp.utils import *
import time
import os

from environs import Env
env = Env()
env.read_env()

"""
环境变量
"""
for key, value in os.environ.items():
    print(f"{key}={value}")

PORT = env.int('PORT', 8080)
RECEIVE_MSG_API = env.str('RECEIVE_MSG_API', '/receive_msg')

YOUDU_BUIN = env.int('YOUDU_BUIN')
YOUDU_APP_ID = env.str('YOUDU_APP_ID')
YOUDU_AES_KEY = env.str('YOUDU_AES_KEY')
YOUDU_CALLBACK_TOKEN = env.str('YOUDU_CALLBACK_TOKEN')
YOUDU_ADDRESS = env.str('YOUDU_ADDRESS', '192.168.8.180:7080')
YOUDU_DOWNLOAD_DIR = env.str('YOUDU_DOWNLOAD_DIR', './download')

OPENAI_EMAIL = env.str('OPENAI_EMAIL')
OPENAI_PWD = env.str('OPENAI_PWD')
OPENAI_KEY = env.str('OPENAI_KEY')
OPENAI_ENGINE = env.str('OPENAI_ENGINE', 'text-davinci-003')
THINKING_TEXT = env.str('THINKING_TEXT', '思考中...')
CHATGPT_PROXY = env.str('CHATGPT_PROXY', None)
SESSION_TIMEOUT = env.int('SESSION_TIMEOUT', 60 * 60 * 3)



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
            if msg.msg_body.content == '/reset':
                reset_session(msg)
            else:    
                await handle_chat(msg)

async def handle_chat(msg):
    if THINKING_TEXT:
        await chatgpt_thinking(msg)
    try:
        if OPENAI_ENGINE == 'chatgpt' :
            await chatgpt_api(msg)
        else:
            await openai_api(msg)
    except Exception as e:
        alert_user_error(msg, e)
        raise e
                
def alert_user_error(msg, e):
    client.send_msg(Message(
        msg.from_user, 
        MESSAGE_TYPE_TEXT, 
        TextBody('''openai api 发生错误: 
%s''' %  e))
    )

def reset_session(msg):
    session = UserSession.get(msg.from_user)
    session.reset()
    client.send_msg(Message(
        msg.from_user, 
        MESSAGE_TYPE_TEXT, 
        TextBody('会话已重置，请重新提问'))
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
    
import abblity
import json
class UserSession:
    def __init__(self, user):
        self.user = user
        self.conversation = []
        self.createtime = time.time()
    
    async def handle_function(self, question, message):
        if message.get("function_call"):
            function_name = message["function_call"]["name"]

            # Step 3, call the function
            # Note: the JSON response from the model may not be valid JSON
            arguments = json.loads(message["function_call"]["arguments"])
            '''apply the function with the arguments'''
            print('arguments:', message["function_call"]["arguments"])
            function_response = await getattr(abblity, function_name)(**arguments, user=self.user)

            # Step 4, send model the info on the function call and function response
            second_response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo-0613",
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    },
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    },
                ],
                functions=abblity.functions,
                function_call="auto"
            )
            return second_response.choices[0].message

    async def chat(self, text):
        print('会话[', self.user ,']询问:', text)
        self.conversation.append({
            'role':'user',
            'content':text
        })
        self.createtime = time.time()
        
        messages = self.conversation.copy()
        messages.append({
            'role':'user',
            'content':'the current time is %s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
        
        # Step 1, send the user's message to the model
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo-0613",
            messages= messages,
            functions=abblity.functions,
            function_call="auto"
        )
        print('gpt是否有返回？', completion is None)
        
        # Step 2, handle function calls
        message = completion.choices[0].message
        message = await self.handle_function(text, message) or message
        
        self.conversation.append(message.to_dict())
        print('会话[', self.user ,']回答:', message.content)
        return message.content
    
    def reset(self):
        self.conversation = []
        self.createtime = time.time()

    @classmethod
    def get(cls, user):
        return SessionCollection.getInstance().get(user)
        

class SessionCollection(dict):
    def __init__(self):
        super().__init__()
        
    def get(self, user, default=None):
        try:
            if user not in self \
            or time.time() - self[user].createtime > SESSION_TIMEOUT:
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
    try:
        completion = await session.chat(msg.msg_body.content)
        client.send_msg(Message(
            msg.from_user, 
            MESSAGE_TYPE_TEXT, 
            TextBody(str(completion).lstrip()))
        )
    except openai.error.OpenAIError as e:
        if str(e).find('maximum context length') > -1:
            session.reset()
            client.send_msg(Message(
                msg.from_user, 
                MESSAGE_TYPE_TEXT, 
                '会话超过最大token数，已重置会话，请重新提问')
            )
        else:
            raise e

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
        traceback.print_exc()
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
