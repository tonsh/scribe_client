# -*- coding: utf-8 -*-

import datetime
import mock
import unittest

from scribe_client import (
    ScribeClient, EntityNotDefinedError, EntityRepeatedError)
from field import BooleanField, IntField, StringField


class AnimalLogger(ScribeClient):
    entity = 'demo.animal'
    name = StringField()
    flying = BooleanField()


class DogLogger(AnimalLogger):
    entity = 'demo.dog'
    orders = ['name', 'legs', 'flying']
    legs = IntField()


class ScribeClientTestCase(unittest.TestCase):

    def test_init(self):
        animal = AnimalLogger()
        animal.name = 'animal'
        animal.legs = 2
        animal.flying = True
        self.assertEqual(animal.name, 'animal')
        self.assertTrue(animal.flying)
        self.assertEqual(animal.legs, 2)

        dog = DogLogger(name='dog', legs=4)
        self.assertEqual(set(dog._fields.keys()),
                         set(['name', 'flying', 'legs']))
        self.assertEqual(dog.name, 'dog')
        self.assertFalse(dog.flying)
        self.assertEqual(dog.legs, 4)

        dog.legs = '3'
        self.assertEqual(dog.legs, 3)

        with mock.patch('scribe_client.datetime') as d:
            d.datetime.now.return_value = datetime.datetime(2016, 5, 18, 15, 39, 34)  # noqa
            self.assertEqual(dog.to_string(),
                             "2016-05-18 15:39:34.000000\tdemo.dog\tname=dog\tlegs=3\tflying=False")  # noqa

        self.assertDictEqual(
            ScribeClient._register,
            {'demo.animal': AnimalLogger, 'demo.dog': DogLogger})

    def test_entity(self):
        class NoEntityLogger(AnimalLogger):
            pass

        with self.assertRaises(EntityNotDefinedError):
            NoEntityLogger()

        class Dog2Logger(AnimalLogger):
            entity = 'demo.dog'

        DogLogger(name='dog', legs=4)
        with self.assertRaises(EntityRepeatedError):
            Dog2Logger(name='dog2')

    def test_parse(self):
        line = "2016-05-18 15:39:34.000000\tdemo.dog\tname=dog\tlegs=3\tflying=False"
        dog = ScribeClient.parse(line)

        self.assertEqual(dog.name, 'dog')
        self.assertFalse(dog.flying)
        self.assertEqual(dog.legs, 3)
        self.assertEqual(dog.log_created_at,
                         datetime.datetime(2016, 5, 18, 15, 39, 34))

        dog = ScribeClient.parse(line, includes=['name', 'legs'],
                                 excludes=['name', 'flying'])

        self.assertEqual(dog.name, '')
        self.assertFalse(dog.flying)
        self.assertEqual(dog.legs, 3)
        self.assertEqual(dog.log_created_at,
                         datetime.datetime(2016, 5, 18, 15, 39, 34))


if __name__ == '__main__':
    unittest.main()
