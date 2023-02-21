# -*- coding: utf-8 -*-

"""
回调签名生成工具
"""

import hashlib

from entapp.utils import *


def generate_signature(token, timestamp, nonce, encrypt):

    """
    从SHA1算法生成安全签名
    :param token: 企业应用回调token
    :param timestamp: 回调时间戳（从URL参数取）
    :param nonce: 回调随机字符串（从URL参数取）
    :param encrypt: 回调json数据的密文字段
    :return: 安全签名

    :type token: unicode or str
    :type timestamp: unicode or str
    :type nonce: unicode or str
    :type encrypt: unicode or str
    :rtype: str
    """
    check_types(token, unicode_str(), str)
    check_types(timestamp, unicode_str(), str)
    check_types(nonce, unicode_str(), str)
    check_types(encrypt, unicode_str(), str)

    sort_list = [pystr(token), pystr(timestamp), pystr(nonce), pystr(encrypt)]
    sort_list.sort()
    sha = hashlib.sha1()
    sha.update(bytestr("".join(sort_list)))
    return sha.hexdigest()
