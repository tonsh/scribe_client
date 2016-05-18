# -*- coding: utf-8 -*-

import datetime


class Empty:
    pass


class ScribeFieldError(Exception):
    pass


class ScribeFieldValidateError(Exception):
    pass


class ScribeField(object):
    _default = None

    def __init__(self, default=Empty):
        self.default = default

    @property
    def has_default(self):
        return self.default is not Empty

    def get_default(self):
        if self.has_default:
            if callable(self.default):
                return self.default()
            return self.default

        return self._default

    def validate(self, value):
        raise NotImplementedError

    def output(self, value):
        return self.validate(value)


class BooleanField(ScribeField):
    _default = False

    def validate(self, value):
        if value is None:
            return False
        if value in (True, False):
            return bool(value)
        if value in ('True', 'true', 't', '1', 1):
            return True
        if value in ('False', 'false', 'f', '0', '', 0):
            return False

        raise ScribeFieldValidateError('value invalid.')


class DateField(ScribeField):

    def validate(self, value):
        """ 支持 %Y-%m-%d 格式的字符串 """
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value

        if isinstance(value, basestring):
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ScribeFieldValidateError('value invalid.')
        raise ScribeFieldValidateError('value invalid.')

    def output(self, value):
        return self.validate(value).strftime("%Y-%m-%d")


class DateTimeField(ScribeField):

    def validate(self, value):
        """ 支持 %Y-%m-%d %H:%M:%S 格式的字符串 """
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        if isinstance(value, basestring):
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ScribeFieldValidateError('value invalid.')
        raise ScribeFieldValidateError('value invalid.')

    def output(self, value):
        return self.validate(value).strftime("%Y-%m-%d %H:%M:%S")


class FloatField(ScribeField):
    pass


class IntField(ScribeField):
    _default = 0

    def validate(self, value):
        if value is None:
            return 0

        try:
            return int(value)
        except (TypeError, ValueError):
            raise ScribeFieldValidateError('value invalid.')


class StringField(ScribeField):
    _default = ''

    def validate(self, value):
        if value is None:
            return ''

        if isinstance(value, unicode):
            return value.encode('utf-8')

        return str(value)
