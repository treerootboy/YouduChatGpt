# -*- coding: utf-8 -*-

"""
消息类型定义
"""

import json
from entapp.error import *
from entapp.utils import *


MESSAGE_TYPE_TEXT = 'text'
MESSAGE_TYPE_IMAGE = 'image'
MESSAGE_TYPE_MPNEWS = 'mpnews'
MESSAGE_TYPE_FILE = 'file'
MESSAGE_TYPE_EXLINK = 'exlink'


class MessageBody(object):
    """
    消息体接口
    """
    def from_json_string(self, json_string):
        """
        从json字符串初始化该body，同时返回自身
        :param json_string: json字符串
        :return: 初始化过的body
        :except ParamParserError: 解析失败

        :type json_string: unicode or str
        :rtype: MessageBody
        """
        raise NotImplemented

    def from_json_object(self, json_object):
        """
        从json对象（字典或列表）初始化该body，同时返回自身
        :param json_object: json对象（字典或列表）
        :return: 初始化过的body
        :except ParamParserError: 字段不存在或类型不匹配

        :type json_object: dict or list
        :rtype: MessageBody
        """
        raise NotImplemented

    def to_json_string(self):
        """
        生成json字符串
        :return: json字符串

        :rtype: str
        """
        raise NotImplemented

    def to_json_object(self):
        """
        生成json对象（字典或列表）
        :return: json对象（字典或列表）

        :rtype: dict or list
        """
        raise NotImplemented

    def to_text_body(self):
        """
        转换为TextBody
        :rtype: TextBody
        """
        if isinstance(self, TextBody):
            return self

        return None

    def to_image_body(self):
        """
        转换为ImageBody
        :rtype: ImageBody
        """
        if isinstance(self, ImageBody):
            return self

        return None

    def to_file_body(self):
        """
        转换为FileBody
        :rtype: FileBody
        """
        if isinstance(self, FileBody):
            return self

        return None

    def to_mpnews_body(self):
        """
        转换为MpnewsBody
        :rtype: MpnewsBody
        """
        if isinstance(self, MpnewsBody):
            return self

        return None

    def to_exlink_body(self):
        """
        转换为ExlinkBody
        :rtype: ExlinkBody
        """
        if isinstance(self, ExlinkBody):
            return self

        return None


class TextBody(MessageBody):
    """
    文字消息
    """

    def __init__(self, content=''):
        """
        构造函数
        :param content: 文字内容

        :type content: unicode or str
        """
        check_types(content, unicode_str(), str)
        self.__content = pystr(content)

    @property
    def content(self):
        """
        文字内容
        :rtype: str
        """
        return self.__content

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return {'content': self.__content}

    def from_json_string(self, json_string):
        check_types(json_string, unicode_str(), str)
        try:
            return self.from_json_object(json_loads_utf8(json_string))
        except ValueError as e:
            raise ParamParserError('decode json failed', e)

    def from_json_object(self, json_object):
        check_type(json_object, dict)
        content = json_object.get('content')
        if not is_instance(content, unicode_str(), str):
            raise ParamParserError('content not exists or not match type bytes and unicode or str')

        self.__content = pystr(content)
        return self

    def __str__(self):
        return 'TextBody:\n' \
               '    content: {content}\n'.format(content=self.__content)


class ImageBody(MessageBody):
    """
    图片消息
    """

    def __init__(self, media_id=''):
        """
        构造函数
        :param media_id: 资源Id

        :type media_id: unicode or str
        """
        check_types(media_id, unicode_str(), str)
        self.__media_id = pystr(media_id)

    @property
    def media_id(self):
        """
        资源Id
        :rtype: str
        """
        return self.__media_id

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return {'media_id': self.__media_id}

    def from_json_string(self, json_string):
        check_types(json_string, unicode_str(), str)
        try:
            return self.from_json_object(json_loads_utf8(json_string))
        except ValueError as e:
            raise ParamParserError('decode json failed', e)

    def from_json_object(self, json_object):
        check_type(json_object, dict)
        media_id = json_object.get('media_id')
        if not is_instance(media_id, unicode_str(), str):
            raise ParamParserError('media_id not exists or type not match type bytes and unicode or str')

        self.__media_id = pystr(media_id)
        return self

    def __str__(self):
        return 'ImageBody:\n' \
               '    media_id: {media_id}\n'.format(media_id=self.__media_id)


class FileBody(MessageBody):
    """
    文件消息
    """

    def __init__(self, media_id=''):
        """
        构造函数
        :param media_id: 资源Id

        :type media_id: unicode or str
        """
        check_types(media_id, unicode_str(), str)
        self.__media_id = pystr(media_id)

    @property
    def media_id(self):
        """
        资源Id
        :rtype: str
        """
        return self.__media_id

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return {'media_id': self.__media_id}

    def from_json_string(self, json_string):
        check_types(json_string, unicode_str(), str)
        try:
            return self.from_json_object(json_loads_utf8(json_string))
        except ValueError as e:
            raise ParamParserError('decode json failed', e)

    def from_json_object(self, json_object):
        check_type(json_object, dict)
        media_id = json_object.get('media_id')
        if not is_instance(media_id, unicode_str(), str):
            raise ParamParserError('media_id not exists or type not match type bytes and unicode or str')

        self.__media_id = pystr(media_id)
        return self

    def __str__(self):
        return 'FileBody:\n' \
               '    media_id: {media_id}\n'.format(media_id=self.__media_id)


class MpnewsBody(MessageBody):
    """
    图文消息
    """

    def __init__(self, msg_list=list()):
        """
        构造函数
        :param msg_list: MpnewsBodyCell列表

        :type msg_list: list of MpnewsBodyCell
        """
        check_type(msg_list, list)
        self.__msg_list = msg_list

    @property
    def msg_list(self):
        """
        MpnewsBodyCell列表
        :rtype: list of MpnewsBodyCell
        """
        return self.__msg_list

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return list(map(lambda cell: cell.to_json_object(), self.__msg_list))

    def __str__(self):
        msg_list = list(map(lambda cell: str(cell), self.__msg_list))
        return 'MpnewsBody:\n' \
               '    msg_list: {msg_list}\n'.format(msg_list=str(msg_list))


class MpnewsBodyCell(MessageBody):
    """
    图文消息cell
    """

    def __init__(self, title='', media_id='', digest='', content=''):
        """
        构造函数
        :param title: 标题
        :param media_id: 封面图片的Id
        :param digest: 摘要
        :param content: 正文

        :type title: unicode or str
        :type media_id: unicode or str
        :type digest: unicode or str
        :type content: unicode or str
        """
        check_types(title, unicode_str(), str)
        check_types(media_id, unicode_str(), str)
        check_types(digest, unicode_str(), str)
        check_types(content, unicode_str(), str)
        self.__title = pystr(title)
        self.__media_id = pystr(media_id)
        self.__digest = pystr(digest)
        self.__content = pystr(content)

    @property
    def title(self):
        """
        标题
        :rtype: str
        """
        return self.__title

    @property
    def media_id(self):
        """
        资源Id
        :rtype: str
        """
        return self.__media_id

    @property
    def digest(self):
        """
        摘要
        :rtype: str
        """
        return self.__digest

    @property
    def content(self):
        """
        正文
        :rtype: str
        """
        return self.__content

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return {'title': self.__title,
                'media_id': self.__media_id,
                'digest': self.__digest,
                'content': self.__content}

    def __str__(self):
        return 'MpnewsBodyCell:\n' \
               '    title: {title},\n' \
               '    media_id: {media_id},\n' \
               '    digest: {digest},\n' \
               '    content: {content}\n'.format(title=self.__title,
                                                 media_id=self.__media_id,
                                                 digest=self.__digest,
                                                 content=self.__content)


class ExlinkBody(MessageBody):
    """
    外链消息
    """

    def __init__(self, msg_list=list()):
        """
        构造函数
        :param msg_list: ExlinkBodyCell列表

        :type msg_list: list of ExlinkBodyCell
        """
        check_type(msg_list, list)
        self.__msg_list = msg_list

    @property
    def msg_list(self):
        """
        ExlinkBodyCell列表
        :rtype: list of ExlinkBodyCell
        """
        return self.__msg_list

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return list(map(lambda cell: cell.to_json_object(), self.__msg_list))

    def __str__(self):
        msg_list = list(map(lambda cell: str(cell), self.__msg_list))
        return 'ExlinkBody:\n' \
               '    msg_list: {msg_list}\n'.format(msg_list=str(msg_list))


class ExlinkBodyCell(MessageBody):
    """
    外链消息cell
    """

    def __init__(self, title='', url='', digest='', media_id=''):
        """
        构造函数
        :param title: 标题
        :param url: 链接
        :param digest: 摘要
        :param media_id: 封面图片的Id

        :type title: unicode or str
        :type url: unicode or str
        :type digest: unicode or str
        :type media_id: unicode or str
        """
        check_types(title, unicode_str(), str)
        check_types(url, unicode_str(), str)
        check_types(digest, unicode_str(), str)
        check_types(media_id, unicode_str(), str)
        self.__title = pystr(title)
        self.__url = pystr(url)
        self.__digest = pystr(digest)
        self.__media_id = pystr(media_id)

    @property
    def title(self):
        """
        标题
        :rtype: str
        """
        return self.__title

    @property
    def url(self):
        """
        正文
        :rtype: str
        """
        return self.__url

    @property
    def digest(self):
        """
        摘要
        :rtype: str
        """
        return self.__digest

    @property
    def media_id(self):
        """
        资源Id
        :rtype: str
        """
        return self.__media_id

    def to_json_string(self):
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        return {'title': self.__title,
                'url': self.__url,
                'digest': self.__digest,
                'media_id': self.__media_id}

    def __str__(self):
        return 'ExlinkBodyCell:\n' \
               '    title: {title},\n' \
               '    url: {url},\n' \
               '    digest: {digest},\n' \
               '    media_id: {media_id}\n'.format(title=self.__title,
                                                   url=self.__url,
                                                   digest=self.__digest,
                                                   media_id=self.__media_id)


class Message(object):
    """
    发送消息类型
    """
    def __init__(self, to_user, msg_type, msg_body):
        """
        构造函数
        :param to_user: 发送目标用户，格式为"user1 | user2 | user3"
        :param msg_type: 消息类型
        :param msg_body: 消息体

        :type to_user: unicode or str
        :type msg_type: str
        :type msg_body: MessageBody
        """
        check_types(to_user, unicode_str(), str)
        check_type(msg_type, str)
        check_types(msg_body, MessageBody)
        self.__to_user = pystr(to_user)
        self.__msg_type = msg_type
        self.__msg_body = msg_body

    @property
    def to_user(self):
        """
        发送目标用户，格式为"user1 | user2 | user3"
        :rtype: str
        """
        return self.__to_user

    @property
    def msg_type(self):
        """
        消息类型
        :rtype: str
        """
        return self.__msg_type

    @property
    def msg_body(self):
        """
        消息体
        :rtype: MessageBody
        """
        return self.__msg_body

    def to_json_string(self):
        """
        生成json字符串
        :rtype: str
        """
        return json.dumps(self.to_json_object())

    def to_json_object(self):
        """
        生成json对象字典
        :rtype: dict
        """
        return {'toUser': self.__to_user,
                'msgType': self.__msg_type,
                self.__msg_type: self.__msg_body.to_json_object()}

    def __str__(self):
        return 'Message:\n' \
               '    to_user: {to_user},\n' \
               '    msg_type: {msg_type},\n' \
               '    msg_body: {msg_body}\n'.format(to_user=self.__to_user,
                                                   msg_type=self.__msg_type,
                                                   msg_body=str(self.__msg_body))


class ReceiveMessage(object):
    """
    接收消息类型
    """

    def __init__(self):
        self.__from_user = ''
        self.__create_time = 0
        self.__package_id = ""
        self.__msg_type = ""
        self.__msg_body = None

    @property
    def from_user(self):
        """
        发送消息的用户账号
        :rtype: str
        """
        return self.__from_user

    @property
    def create_time(self):
        """
        发送时间戳，单位：秒
        :rtype: int
        """
        return self.__create_time

    @property
    def package_id(self):
        """
        package id 需要返回给有度服务器
        :rtype: str
        """
        return self.__package_id

    @property
    def msg_type(self):
        """
        消息类型
        :rtype: str
        """
        return self.__msg_type

    @property
    def msg_body(self):
        """
        消息体
        :rtype: MessageBody
        """
        return self.__msg_body

    def from_json_string(self, json_string):
        """
        从json字符串初始化对象，同时返回自身
        :param json_string: json字符串
        :return: 初始化过对象
        :except ParamParserError: 解析失败

        :type json_string: unicode or str
        :rtype: ReceiveMessage
        """
        check_types(json_string, unicode_str(), str)
        try:
            return self.from_json_object(json_loads_utf8(json_string))
        except ValueError as e:
            raise ParamParserError('decode json failed', e)

    def from_json_object(self, json_object):
        """
        从json对象（字典或列表）初始化对象，同时返回自身
        :param json_object: json对象（字典或列表）
        :return: 初始化过的对象
        :except ParamParserError: 字段不存在或类型不匹配

        :type json_object: dict
        :rtype: ReceiveMessage
        """
        check_type(json_object, dict)
        from_user = json_object.get('fromUser')
        if not is_instance(from_user, unicode_str(), str):
            raise ParamParserError('fromUser not exists or type not match type bytes and unicode or str')

        self.__from_user = pystr(from_user)

        create_time = json_object.get('createTime')
        if not isinstance(create_time, int):
            raise ParamParserError('createTime not exists or type not match type bytes and unicode or str')

        self.__create_time = create_time

        package_id = json_object.get('packageId')
        if not is_instance(package_id, unicode_str(), str):
            raise ParamParserError('packageId not exists or type not match type bytes and unicode or str')

        self.__package_id = pystr(package_id)

        msg_type = json_object.get('msgType')
        if not is_instance(msg_type, unicode_str(), str):
            raise ParamParserError('msgType not exists or type not match type bytes and unicode or str')

        self.__msg_type = pystr(msg_type)

        msg_body_object = json_object.get(msg_type)
        if not isinstance(msg_body_object, dict):
            raise ParamParserError('{msg_type} not exists or type not match type '
                                   'bytes and unicode or str'.format(msg_type=pystr(msg_type)))

        if self.__msg_type == MESSAGE_TYPE_TEXT:
            self.__msg_body = TextBody().from_json_object(msg_body_object)
        elif self.__msg_type == MESSAGE_TYPE_IMAGE:
            self.__msg_body = ImageBody().from_json_object(msg_body_object)
        elif self.__msg_type == MESSAGE_TYPE_FILE:
            self.__msg_body = FileBody().from_json_object(msg_body_object)
        else:
            raise ParamParserError('unsupported message type: {msg_type}'.format(msg_type=self.msg_type))

        return self

    def __str__(self):
        return 'ReceiveMessage:\n' \
               '    from_user: {from_user},\n' \
               '    create_time: {create_time},\n' \
               '    package_id: {package_id},\n' \
               '    msg_type: {msg_type},\n' \
               '    msg_body: {msg_body}\n'.format(from_user=self.__from_user,
                                                   create_time=self.__create_time,
                                                   package_id=self.__package_id,
                                                   msg_type=self.__msg_type,
                                                   msg_body=str(self.__msg_body))
