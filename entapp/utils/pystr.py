# -*- coding: utf-8 -*-

"""
兼容python2和python3的字符串与字节数组的转换函数
"""

from platform import python_version_tuple
import json


PYTHON_VERSION = int(python_version_tuple()[0])


def bytestr(text):
    """
    字符串转字节数组，使用utf-8编码
    :param text: 字符串，python2为unicode，python3为str
    :return: 字节数组

    :type text: str or unicode or string
    :rtype: bytes
    """
    if PYTHON_VERSION < 3:
        if isinstance(text, str):
            return text
        elif isinstance(text, unicode):
            return text.encode(encoding='utf_8', errors='strict')
        else:
            raise TypeError('the value does not match type: str or unicode')
    else:
        if isinstance(text, str):
            return text.encode(encoding='utf_8', errors='strict')
        elif isinstance(text, bytes):
            return text
        else:
            raise TypeError('the value does not match type: str or bytes')


def unistr(text):
    """
    字节数组转字符串，使用utf-8编码
    :param text: 字节数组
    :return: 字符串，python2为unicode，python3为str

    :type text: bytes or unicode or string
    :rtype: str
    """
    if PYTHON_VERSION < 3:
        if isinstance(text, bytes):
            return text.decode(encoding='utf_8', errors='strict')
        elif isinstance(text, unicode):
            return text
        else:
            raise TypeError('the value does not match type bytes and unicode')
    else:
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode(encoding='utf_8', errors='strict')
        else:
            raise TypeError('the value does not match type: str or bytes')


def pystr(text):
    """
    转化成python2或python3的str类型，
    :param text: 字符串或字节数组
    :return: str对象

    :type text: bytes or unicode or str
    :rtype: str
    """
    if PYTHON_VERSION < 3:
        if isinstance(text, bytes):
            return text
        elif isinstance(text, unicode):
            return text.encode(encoding='utf_8', errors='strict')
        else:
            raise TypeError('the value does not match type: bytes or unicode')
    else:
        if isinstance(text, bytes):
            return text.decode(encoding='utf_8', errors='strict')
        elif isinstance(text, str):
            return text
        else:
            raise TypeError('the value does not match type: str or bytes')


def unicode_str():
    """
    unicode字符串类型
    python2 返回unicode，python3返回str
    :return: 类型

    :rtype: cls
    """
    if PYTHON_VERSION < 3:
        return unicode
    else:
        return str


def json_loads_utf8(json_string):
    """
    反序列化json字符串，用UTF-8编码
    :param json_string: json字符串
    :return: json对象（字典或列表）

    :type json_string: unicode or str
    :rtype: dict or list
    """
    if isinstance(json_string, str) or isinstance(json_string, unicode_str()):
        return json.loads(json_string)
    else:
        raise TypeError('the value does not match type: str or unicode')

