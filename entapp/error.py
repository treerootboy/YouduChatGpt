# -*- coding: utf-8 -*-

"""
错误类型
"""


class GeneralEntAppError(Exception):
    """
    通用错误类型
    """

    def __init__(self, message, cause=None):
        """
        构造函数
        :type message: str
        :type cause: Exception
        :param message: 异常信息
        :param cause: 引发该问题的异常
        """
        self.__message = message
        self.__cause = cause

    @property
    def message(self):
        """
        异常信息
        :rtype: str
        """
        return self.__message

    @property
    def cause(self):
        """
        引发该问题的异常
        :rtype: Exception
        """
        return self.__cause

    def __str__(self, *args, **kwargs):
        return '{base_err}\n    message: {message}\n    cause: {cause}\n'.format(
            base_err=super().__str__(*args, **kwargs), message=self.__message, cause=self.__cause)


class AESCryptoError(GeneralEntAppError):
    """
    AES加解密错误
    """
    pass


class FileIOError(GeneralEntAppError):
    """
    文件读写错误
    """
    pass


class HttpRequestError(GeneralEntAppError):
    """
    HTTP请求错误
    """

    def __init__(self, code, message, cause=None):
        """
        构造函数
        :type code: int
        :type message: str
        :type cause: Exception
        :param code: 错误码
        :param message: 错误信息
        :param cause: 引发该问题的异常
        """
        super(HttpRequestError, self).__init__(message, cause)
        self.__code = code

    @property
    def code(self):
        """
        错误码
        :rtype: int
        """
        return self.__code

    def __str__(self, *args, **kwargs):
        return '{base_err}\n    code: {code}\n'.format(
            base_err=super().__str__(*args, **kwargs), code=self.__code)


class ParamParserError(GeneralEntAppError):
    """
    参数解析错误
    """
    pass


class ServiceError(GeneralEntAppError):
    """
    服务出现问题
    """
    pass


class SignatureError(GeneralEntAppError):
    """
    签名校验错误
    """
    pass
