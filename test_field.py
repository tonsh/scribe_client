# -*- coding: utf-8 -*-

import datetime
import unittest

from field import (
    BooleanField, IntField, DateField, DateTimeField, ScribeField,
    ScribeFieldValidateError, StringField)


class DemoField(ScribeField):
    pass


class ScribeFieldTestCase(unittest.TestCase):

    def test_default(self):
        f = DemoField()
        self.assertFalse(f.has_default)
        self.assertIsNone(f.get_default())

        DemoField._default = 'hello world'
        f = DemoField()
        self.assertFalse(f.has_default)
        self.assertEqual(f.get_default(), 'hello world')

        f = DemoField(default='hello')
        self.assertEqual(f.get_default(), 'hello')

        f = DemoField(default=lambda: 'world')
        self.assertEqual(f.get_default(), 'world')

    def test_boolean_field(self):
        f = BooleanField(default=True)
        self.assertTrue(f.get_default())

        f = BooleanField()
        self.assertFalse(f.get_default())

        for v in [True, 'true', 'True', 't', '1', 1]:
            self.assertTrue(f.validate(v))

        for v in [False, 'false', 'False', 'f', '0', '', 0, None]:
            self.assertFalse(f.validate(v))

        with self.assertRaises(ScribeFieldValidateError):
            f.validate('hello')

    def test_int_field(self):
        f = IntField(default=10)
        self.assertEqual(f.get_default(), 10)

        f = IntField()
        self.assertEqual(f.get_default(), 0)

        self.assertEqual(f.validate(None), 0)
        for v in [1, '1']:
            self.assertEqual(f.validate(v), 1)

        with self.assertRaises(ScribeFieldValidateError):
            f.validate('i1')

    def test_string_field(self):
        f = StringField(default='abc')
        self.assertEqual(f.get_default(), 'abc')

        f = StringField()
        self.assertEqual(f.get_default(), '')

        self.assertEqual(f.validate(None), '')
        self.assertEqual(f.validate('1'), '1')
        self.assertEqual(f.validate(u'一'), '一')
        self.assertEqual(f.validate(1), '1')

    def test_date_field(self):
        f = DateField(default=datetime.date.today())
        self.assertEqual(f.get_default(), datetime.date.today())

        f = DateField()
        self.assertIsNone(f.get_default())

        today = datetime.date.today()
        self.assertEqual(f.validate(today), today)

        now = datetime.datetime.now()
        self.assertEqual(f.validate(now), now.date())
        self.assertEqual(f.validate('2016-05-18'),
                         datetime.date(2016, 5, 18))

        self.assertEqual('2016-05-18', f.output('2016-05-18'))

        with self.assertRaises(ScribeFieldValidateError):
            f.validate(123)
        with self.assertRaises(ScribeFieldValidateError):
            f.validate('16-05-18')

    def test_datetime_field(self):
        d = datetime.datetime(2016, 5, 18, 18, 42, 34)
        f = DateTimeField(default=d)
        self.assertEqual(f.get_default(), d)

        f = DateTimeField()
        self.assertIsNone(f.get_default())

        today = datetime.date(2016, 5, 18)
        self.assertEqual(f.validate(today), datetime.datetime(2016, 5, 18))
        self.assertEqual(f.validate(d), d)
        self.assertEqual(f.validate('2016-05-18 18:42:34'),
                         datetime.datetime(2016, 5, 18, 18, 42, 34))

        self.assertEqual('2016-05-18 00:00:00', f.output(today))

        with self.assertRaises(ScribeFieldValidateError):
            f.validate(123)
        with self.assertRaises(ScribeFieldValidateError):
            f.validate('16-05-18')

if __name__ == '__main__':
    unittest.main()
