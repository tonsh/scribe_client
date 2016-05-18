# -*- coding: utf-8 -*-

import datetime

from field import ScribeField


class ScribeClientError(Exception):
    pass


class EntityNotDefinedError(Exception):
    pass


class EntityRepeatedError(Exception):
    pass


class ScribeClient(object):
    """ scribe 日志发送及解析类 """
    SEPARATOR = '\t'
    BINDING = "="
    entity = ''
    orders = []
    _register = {}

    def __new__(cls, *args, **kwargs):
        if not cls.__dict__.get('entity'):
            raise EntityNotDefinedError('Not define entity.')

        # 注册器，用于维护 entity 与类的对应关系，解析日志时可通过 entity 返回对应的日志对象
        if cls.entity in ScribeClient._register:
            if cls.__name__ != ScribeClient._register[cls.entity].__name__:
                raise EntityRepeatedError('Entity %s has exist.' % cls.entity)
        ScribeClient._register[cls.entity] = cls

        fields = {}
        for parent in cls.mro():
            for key, val in parent.__dict__.items():
                if isinstance(val, ScribeField) and key not in fields:
                    fields[key] = val

        if not fields:
            raise ScribeClientError('Not define fields.')

        cls._fields = fields

        return super(ScribeClient, cls).__new__(cls, args, kwargs)

    def __init__(self, **kwargs):
        self.created_at = None

        for key, field_obj in self._fields.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, field_obj.get_default())

    def __setattr__(self, key, value):
        if key in self._fields:
            value = self._fields[key].validate(value)
        super(ScribeClient, self).__setattr__(key, value)

    @classmethod
    def _check_orders(cls):
        if cls.orders:
            for key in cls.orders:
                if key not in cls._fields:
                    raise ScribeClientError('order key not exist.')

    @staticmethod
    def get_logger_by_entity(entity, **kwargs):
        cls_name = ScribeClient._register.get(entity)
        if not cls_name:
            raise Exception('Entity %s has not be registered.' % entity)

        return cls_name(**kwargs)

    def to_string(self):
        self._check_orders()

        # 第一列为日记写入（发送）时间
        now = datetime.datetime.now()
        msg = [now.strftime("%Y-%m-%d %H:%M:%S.%f")]

        # 第二列为日志标识
        msg.append(self.entity)

        orders = self.orders or self._fields.keys()
        for key in orders:
            value = getattr(self, key)
            msg.append("%s%s%s" % (key, self.BINDING,
                                   self._fields[key].output(value)))

        msg = map(lambda x: x.replace('\t', ' '), msg)
        return self.SEPARATOR.join(msg)

    def send(self):
        """ 日志发送 """
        msg = self.to_string()
        # TODO send msg to scribe server

    @classmethod
    def parse(cls, line, includes=None, excludes=None):
        """ 日志解析，line 需与 to_string() 生成的格式相同 """
        line = line.split(cls.SEPARATOR)
        created_at = datetime.datetime.strptime(
            line[0], "%Y-%m-%d %H:%M:%S.%f")
        entity = line[1]

        fields = []
        for item in line[2:]:
            key, value = item.split(cls.BINDING)
            fields.append((key, value))

        if excludes:
            fields = filter(lambda x: x[0] not in excludes, fields)
        if includes:
            fields = filter(lambda x: x[0] in includes, fields)

        obj = cls.get_logger_by_entity(entity, **dict(fields))
        obj.log_created_at = created_at
        return obj
