# -*- coding: utf-8 -*-

"""
主动调用接口
"""

import json
import time
from os.path import join, abspath

import requests
from requests_toolbelt import MultipartEncoder

from .api import *
from entapp.aes import AESCrypto
from entapp.error import *
from entapp.message import Message
from entapp.utils import *


FILE_TYPE_FILE = 'file'
FILE_TYPE_IMAGE = 'image'


class AppClient(object):
    """
    企业应用主动调用接口客户端
    """

    def __init__(self, buin, app_id, aes_key, address):
        """
        构造函数
        :param buin: 企业总机号
        :param app_id: AppId
        :param aes_key: encodingaeskey
        :param address: 有度服务器地址（IP:PORT）

        :type buin: int
        :type app_id: unicode or str
        :type aes_key: unicode or str
        :type address: unicode or str
        """
        check_type(buin, int)
        check_types(app_id, unicode_str(), str)
        check_types(aes_key, unicode_str(), str)
        check_types(address, unicode_str(), str)
        self.__buin = buin
        self.__app_id = pystr(app_id)
        self.__address = pystr(address)
        self.__crypto = AESCrypto(app_id, aes_key)
        self.__token_info = None

    @property
    def buin(self):
        """
        企业总机号
        :rtype: int
        """
        return self.__buin

    @property
    def app_id(self):
        """
        AppId
        :rtype: str
        """
        return self.__app_id

    @property
    def address(self):
        """
        有度服务器地址（IP:PORT）
        :rtype: str
        """
        return self.__address

    def __check_and_refresh_token(self):
        """
        检查token，不存在或者过期则取获取一次token
        """
        now = int(time.time())
        if self.__token_info is None or self.__token_info[1] + self.__token_info[2] < now:
            token_url = '{scheme}{address}{uri}'.format(
                scheme=SCHEME, address=self.__address, uri=API_GET_TOKEN)
            access_token, expire_in = _get_token(self.__buin, self.__app_id, token_url, self.__crypto)
            self.__token_info = (access_token, expire_in, now)

    def send_msg(self, msg):
        """
        发送消息
        :param msg: 消息对象
        :except AESCryptoError: 加密失败
        :except ParamParserError: 参数解析错误
        :except HttpRequestError: http请求错误

        :type msg: Message
        """
        check_type(msg, Message)
        self.__check_and_refresh_token()
        url = _url_with_token(self.__address, API_SEND_MSG, self.__token_info[0])
        _send_msg(self.__buin, self.__app_id, url, self.__crypto, msg)

    def upload_file(self, file_type, file_name, file_path):
        """
        上传文件
        :param file_type: 文件类型
        :param file_name: 文件名称
        :param file_path: 文件路径
        :return: 资源Id
        :except AESCryptoError: 加密失败
        :except ParamParserError: 参数解析错误
        :except HttpRequestError: http请求错误
        :except FileIOError: 读文件错误

        :type file_type: str
        :type file_name: unicode or str
        :type file_path: unicode or str
        :rtype: str
        """
        check_type(file_type, str)
        check_types(file_name, unicode_str(), str)
        check_types(file_path, unicode_str(), str)
        self.__check_and_refresh_token()
        url = _url_with_token(self.__address, API_UPLOAD_FILE, self.__token_info[0])
        return _upload_file(self.__buin, self.__app_id, url, self.__crypto, file_type, pystr(file_name), pystr(file_path))

    def download_file(self, media_id, out_dir):
        """
        下载文件
        :param media_id: 资源Id
        :param out_dir: 输出文件的目录
        :return: (name: 文件名称, size: 文件大小，单位：字节, content: 文件内容)
        :except AESCryptoError: 加密失败
        :except ParamParserError: 参数解析错误
        :except HttpRequestError: http请求错误
        :except FileIOError: 写文件错误

        :type media_id: unicode or str
        :type out_dir: unicode or str
        :rtype: (str, int, bytes)
        """
        check_types(media_id, unicode_str(), str)
        check_types(out_dir, unicode_str(), str)
        self.__check_and_refresh_token()
        url = _url_with_token(self.__address, API_DOWNLOAD_FILE, self.__token_info[0])
        return _download_file(self.__buin, self.__app_id, url, self.__crypto, pystr(media_id), pystr(out_dir))

    def search_file(self, media_id):
        """
        搜索文件信息
        :param media_id: 资源Id
        :return: (文件名, 字节数大小)
        :except AESCryptoError: 加密失败
        :except ParamParserError: 参数解析错误
        :except HttpRequestError: http请求错误

        :type media_id: unicode or str
        :rtype: (str, int)
        """
        check_types(media_id, unicode_str(), str)
        self.__check_and_refresh_token()
        url = _url_with_token(self.__address, API_SEARCHE_FILE, self.__token_info[0])
        return _search_file(self.__buin, self.__app_id, url, self.__crypto, pystr(media_id))


def _url_with_token(address, uri, token):
    """
    生成带Token的url
    :param address: 服务器地址（IP:PORT）
    :param uri: 接口
    :param token: token
    :return: URL

    :type address: str
    :type uri: str
    :type token: str
    :rtype: str
    """
    return '{scheme}{address}{uri}?accessToken={token}'.format(
        scheme=SCHEME, address=address, uri=uri, token=token)


def _parse_status(rsp):

    """
    解析接口错误码
    :param rsp: requests返回的请求结果
    :except HttpRequestError: 失败则抛出异常
    """
    if rsp.status_code != requests.codes.OK:
        try:
            rsp.raise_for_status()
        except requests.HTTPError as e:
            raise HttpRequestError(rsp.status_code, 'request failed', e)


def _parse_err(resp_json):

    """
    解析错误json信息，如果有错误直接抛出异常
    :param resp_json: 接口返回的json信息
    :except ParamParserError: resp_json不为dict抛出异常
    :except HttpRequestError: 错误码不为0则抛出异常
    """
    if not isinstance(resp_json, dict):
        raise ParamParserError('response json is empty')

    err_code = resp_json.get('errcode')
    if not isinstance(err_code, int):
        raise ParamParserError('errcode not match type int')

    if err_code != 0:
        err_msg = resp_json.get('errmsg', 'no error message')
        raise HttpRequestError(err_code, pystr(err_msg))


def _get_token(buin, app_id, url, crypto_obj):
    """
    获取accessToken
    :param buin: 企业总机号
    :param app_id: AppId
    :param url: 请求url
    :param crypto_obj: 加密对象
    :return: (token: accessToken, expire_in: 留存时间，单位：秒)
    :except AESCryptoError: 加密失败
    :except ParamParserError: 参数解析错误
    :except HttpRequestError: http请求错误

    :type buin: int
    :type app_id: str
    :type url: str
    :type crypto_obj: AESCrypto
    :rtype: (str, int)
    """
    cipher_text = crypto_obj.encrypt(bytestr(str(int(time.time()))))
    param = {'buin': buin, 'appId': app_id, 'encrypt': cipher_text}
    json_result = dict()
    try:
        rsp = requests.post(url, json=param)
        _parse_status(rsp)
        json_result = rsp.json()
        _parse_err(json_result)
    except requests.RequestException as e:
        raise HttpRequestError(0, 'connect failed', e)
    except ValueError as e:
        raise ParamParserError('failed to decode json', e)

    encrypt_string = json_result.get('encrypt')
    if not is_instance(encrypt_string, unicode_str(), str):
        raise ParamParserError('encrypt content not exists')

    try:
        token_info = json_loads_utf8(pystr(crypto_obj.decrypt(encrypt_string)))
        token = token_info.get('accessToken')
        expire_in = token_info.get('expireIn')
        if not is_instance(token, unicode_str(), str) and not isinstance(expire_in, int):
            raise ParamParserError('accessToken or expireIn not exists')

        return pystr(token), expire_in
    except ValueError as e:
        raise ParamParserError('parse json failed ', e)


def _send_msg(buin, app_id, url, crypto_obj, msg):
    """
    发送消息
    :param buin: 企业总机号
    :param app_id: AppId
    :param url: 带token的请求URL
    :param crypto_obj: 加密对象
    :param msg: Message消息对象
    :except AESCryptoError: 加密失败
    :except ParamParserError: 参数解析错误
    :except HttpRequestError: http请求错误

    :type buin: int
    :type app_id: str
    :type url: str
    :type crypto_obj: AESCrypto
    :type msg: Message
    """
    cipher_text = crypto_obj.encrypt(bytestr(msg.to_json_string()))
    param = {'buin': buin, 'appId': app_id, 'encrypt': cipher_text}
    try:
        rsp = requests.post(url, json=param)
        _parse_status(rsp)
        _parse_err(rsp.json())
    except requests.RequestException as e:
        raise HttpRequestError(0, 'connect failed', e)
    except ValueError as e:
        raise ParamParserError('failed to decode json', e)


def _upload_file(buin, app_id, url, crypto_obj, file_type, file_name, file_path):
    """
    上传文件
    :param buin: 企业总机号
    :param app_id: AppId
    :param url: 带token的请求URL
    :param crypto_obj: 加密对象
    :param file_type: 文件类型
    :param file_name: 文件名称
    :param file_path: 文件路径
    :return: 资源Id
    :except AESCryptoError: 加密失败
    :except ParamParserError: 参数解析错误
    :except HttpRequestError: http请求错误
    :except FileIOError: 读文件错误

    :type buin: int
    :type app_id: str
    :type url: str
    :type crypto_obj: AESCrypto
    :type file_type: str
    :type file_name: str
    :type file_path: str
    :rtype: str
    """
    cipher_request = crypto_obj.encrypt(bytestr(json.dumps({'type': file_type, 'name': file_name})))
    encrypt_file = ''
    try:
        with open(file_path, 'rb') as f:
            encrypt_file = crypto_obj.encrypt(f.read())
    except IOError as e:
        raise FileIOError('failed to read from file {path}'.format(path=file_path), e)

    encoder = MultipartEncoder(
        fields={'buin': str(buin),
                'appId': app_id,
                'encrypt': cipher_request,
                'file': ('file', encrypt_file, 'text/plain')}
    )

    try:
        rsp = requests.post(url, data=encoder, headers={'Content-Type': encoder.content_type})
        _parse_status(rsp)
        json_result = rsp.json()
        _parse_err(json_result)
        cipher_id = json_result.get('encrypt')
        if not is_instance(cipher_id, unicode_str(), str):
            raise ParamParserError('encrypt content not exists')

        media_id = json_loads_utf8(pystr(crypto_obj.decrypt(cipher_id))).get('mediaId', '')
        if not is_instance(media_id, unicode_str(), str):
            raise ParamParserError('result invalid')

        return pystr(media_id)
    except requests.RequestException as e:
        raise HttpRequestError(0, 'connect failed', e)
    except ValueError as e:
        raise ParamParserError('failed to decode json', e)


def _download_file(buin, app_id, url, crypto_obj, media_id, out_dir):
    """
    下载文件
    :param buin: 企业总机号
    :param app_id: AppId
    :param url: 带token的请求URL
    :param crypto_obj: 加密对象
    :param media_id: 资源Id
    :param out_dir: 输出文件的目录
    :return: (name: 文件名称, size: 文件大小，单位：字节, content: 文件内容)
    :except AESCryptoError: 加密失败
    :except ParamParserError: 参数解析错误
    :except HttpRequestError: http请求错误
    :except FileIOError: 写文件错误

    :type buin: int
    :type app_id: str
    :type url: str
    :type crypto_obj: AESCrypto
    :type media_id: str
    :type out_dir: str
    :rtype: (str, int, bytes)
    """
    cipher_id = crypto_obj.encrypt(bytestr(json.dumps({'mediaId': media_id})))
    param = {'buin': buin, 'appId': app_id, 'encrypt': cipher_id}
    try:
        rsp = requests.post(url, json=param)
        _parse_status(rsp)
        json_result = None
        try:
            json_result = rsp.json()
        except ValueError:
            pass  # 成功的时候不存在JSON数据
        if json_result is None:
            json_result = {'errcode': 0, 'errmsg': ''}
        _parse_err(json_result)
        cipher_info = rsp.headers.get('encrypt')
        if not is_instance(cipher_info, unicode_str(), str):
            raise ParamParserError('encrypt content not exists')

        file_info = json_loads_utf8(pystr(crypto_obj.decrypt(cipher_info)))
        file_name = file_info.get('name')
        file_size = file_info.get('size')
        if not is_instance(file_name, unicode_str(), str) and isinstance(file_size, int):
            raise ParamParserError('name or size not exists')

        file_content = bytestr('')
        with open(abspath(join(out_dir, pystr(file_name))), 'wb') as f:
            file_content = crypto_obj.decrypt(pystr(rsp.content))
            f.write(file_content)

        return pystr(file_name), file_size, file_content

    except requests.RequestException as e:
        raise HttpRequestError(0, 'connect failed', e)
    except ValueError as e:
        raise ParamParserError('failed to decode json', e)
    except IOError as e:
        raise FileIOError('failed to save file to {path}'.format(path=out_dir), e)


def _search_file(buin, app_id, url, crypto_obj, media_id):
    """
    搜索文件信息
    :param buin: 企业总机号
    :param app_id: AppId
    :param url: 带token的请求URL
    :param crypto_obj: 加密对象
    :param media_id: 资源Id
    :return: (文件名, 字节数大小)
    :except AESCryptoError: 加密失败
    :except ParamParserError: 参数解析错误
    :except HttpRequestError: http请求错误

    :type buin: int
    :type app_id: str
    :type url: str
    :type crypto_obj: AESCrypto
    :type media_id: str
    :rtype: (str, int)
    """
    cipher_id = crypto_obj.encrypt(bytestr(json.dumps({'mediaId': media_id})))
    param = {'buin': buin, 'appId': app_id, 'encrypt': cipher_id}
    try:
        rsp = requests.post(url, json=param)
        _parse_status(rsp)
        json_result = rsp.json()
        _parse_err(json_result)
        encrypt_result = json_result.get('encrypt')
        if not is_instance(encrypt_result, unicode_str(), str):
            raise ParamParserError('encrypt content not exists')

        file_info = json_loads_utf8(pystr(crypto_obj.decrypt(encrypt_result)))
        name = file_info.get('name', '')
        size = file_info.get('size', 0)
        if name == '' or size <= 0:
            raise ParamParserError('file info is not valid')

        return name, size
    except requests.RequestException as e:
        raise HttpRequestError(0, 'connect failed', e)
    except ValueError as e:
        raise ParamParserError('failed to decode json', e)
