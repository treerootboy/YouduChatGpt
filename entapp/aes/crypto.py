# -*- coding: utf-8 -*-

"""
加解密工具
"""

from Crypto.Cipher import AES
from Crypto import Random
import base64
import struct
from entapp.error import AESCryptoError

from entapp.utils import *


class AESCrypto(object):
    """
    AES加解密工具类
    """

    def __init__(self, app_id, key):
        """
        构造函数
        :param app_id: AppId
        :param key: AES Key

        :type app_id: unicode or str
        :type key: unicode or str
        """
        check_types(key, unicode_str(), str)
        check_types(app_id, unicode_str(), str)

        self.__key = pystr(key)
        self.__app_id = pystr(app_id)

    @property
    def key(self):
        """
        AES Key
        :rtype: str
        """
        return self.__key

    @property
    def app_id(self):
        """
        AppId
        :rtype: str
        """
        return self.__app_id

    def encrypt(self, input_data):
        """
        AES加密
        :param input_data: 明文
        :return: 密文
        :except AESCryptoError: 加密失败

        :type input_data: bytes
        :rtype: str
        """
        check_type(input_data, bytes)
        return _encrypt(self.__key, self.__app_id, input_data)

    def decrypt(self, input_string):
        """
        AES解密
        :param input_string: 密文
        :return: 明文
        :except AESCryptoError: 解密失败

        :type input_string: unicode or str
        :rtype: bytes
        """
        check_types(input_string, unicode_str(), str)
        return _decrypt(self.__key, self.__app_id, input_string)


__AES_PADDING = 32


def _encrypt(key, app_id, input_data):
    """
    AES加密
    :param key: AES Key
    :param app_id: AppId
    :param input_data: 明文
    :return: 密文
    :except AESCryptoError: 加密失败

    :type key: unicode or str
    :type app_id: unicode or str
    :type input_data: bytes
    :rtype: str
    """
    try:
        rand_str = Random.new().read(16)
        msg_len = struct.pack('!i', len(input_data))
        padded_key = base64.b64decode(key)
        aes = AES.new(padded_key, mode=AES.MODE_CBC, IV=rand_str)
        text = rand_str + msg_len + input_data + bytestr(app_id)
        padded_text = struct.pack('{n}s'.format(
            n=(len(text) // __AES_PADDING + 1) * __AES_PADDING), text)
        padding_len = __AES_PADDING - len(text) % __AES_PADDING
        padded_text = padded_text[0:-padding_len] + struct.pack('b', padding_len) * padding_len
        cipher_text = aes.encrypt(padded_text)
        return pystr(base64.b64encode(cipher_text))
    except Exception as e:
        raise AESCryptoError("encrypt failed", e)


def _decrypt(key, app_id, input_string):
    """
    AES解密
    :param key: AES key
    :param app_id: AppId
    :param input_string: 密文
    :return: 明文
    :except AESCryptoError: 解密失败

    :type key: unicode or str
    :type app_id: unicode or str
    :type input_string: unicode or str
    :rtype: bytes
    """
    try:
        cipher_text = base64.b64decode(input_string)
        padded_key = base64.b64decode(key)
        rand_str = Random.new().read(16)
        aes = AES.new(padded_key, mode=AES.MODE_CBC, IV=rand_str)
        text = aes.decrypt(cipher_text)
        padding_len = text[len(text) - 1]
        if isinstance(padding_len, str):
            padding_len = ord(padding_len)
        text = text[0:-padding_len]
        if len(text) <= 20:
            raise AESCryptoError('invalid msg')

        msg_len = struct.unpack('!i', text[16:20])[0]
        if len(text) <= 20 + msg_len:
            raise AESCryptoError('invalid msg')

        dest_app_id = text[20 + msg_len:]
        if dest_app_id != bytestr(app_id):
            raise AESCryptoError('unmatched AppID: {app_id}'.format(app_id=pystr(dest_app_id)))

        return text[20:20 + msg_len]
    except Exception as e:
        raise AESCryptoError('decrypt failed', e)
