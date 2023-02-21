# -*- coding: utf-8 -*-

"""
类型相关工具
"""


def check_type(value, value_type):
    """
    检查值类型是否匹配，不匹配则抛出TypeError
    :param value: 值
    :param value_type: 类型

    :type value: object
    :type value_type: cls
    """
    if not isinstance(value, value_type):
        raise TypeError('the value does not match type {value_type}'.format(value_type=value_type))


def check_types(value, *value_types):
    """
    检查值类型是否匹配，不匹配则抛出TypeError
    :param value: 值
    :param value_types: 类型列表

    :type value: object
    :type value_types: list of cls
    """
    for t in value_types:
        if isinstance(value, t):
            return

    raise TypeError('the value does not match type {value_types}'.format(value_types=str(value_types)))


def is_instance(value, *value_types):
    """
    值是否是该类型的实例
    :param value: 值
    :param value_types: 类型列表
    :return: 是或否

    :type value: object
    :type value_types: list of cls
    :rtype: bool
    """
    for t in value_types:
        if isinstance(value, t):
            return True

    return False
