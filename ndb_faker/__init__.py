# -*- coding: utf-8 -*-
"""
    NDB Faker
    ~~~~~~~~~

    NDB Model & Properties for creating entities with fake data.

    :license: MIT License, see LICENSE for more details.
    :documentation: See README.md for documentation.

"""

__version__ = '1.0'

from google.appengine.ext import ndb
from google.appengine.api import users

import datetime
import hashlib
import random
import uuid

try:
    from faker import Faker, numerify, patterns
except ImportError:
    raise RuntimeError(
        'Faker module required: https://github.com/deepthawtz/faker\n\
        This package includes the Faker module as git submodule.\n\
        Simply swap the inner "faker" folder with the outer "faker" folder.')

# --------------------------------------------------------------------
# Faker
# --------------------------------------------------------------------

class Faker(Faker):
    """ Simply subclassing and adding a few more methods """

    phone_number = Faker.phonenumber
    address      = Faker.street_address

    def zip(self):
        return int(numerify("#####"))

    def ssn(self):
        return numerify("###-##-#####")

    def website(self):
        return 'http://%s.%s' % (patterns.COMPANY_NAME().lower().replace(' ', '-'),
                                 random.choice(['com','net','org']))

    def guid(self):
        return str(uuid.uuid4())

    def md5(self):
        return hashlib.md5(str(random.random())).hexdigest()

    def sha1(self):
        return hashlib.sha1(str(random.random())).hexdigest()

    def caption(self):
        return self.lorem()[0:64]

    def latitude(self):
        geo = (random.randint(-180000000, 180000000) / 1000000.0) / 2
        return float('%0.2f' % geo)

    def longitude(self):
        geo = random.randint(-180000000, 180000000) / 1000000.0
        return float('%0.2f' % geo)

    def coordinates(self):
        return ndb.GeoPt('%f,%f' % (self.latitude(), self.longitude()))

    def profile(self):
        return dict(
            first_name = self.first_name(),
            last_name = self.last_name(),
            username = self.username(),
            email = self.email(),
            full_address = self.full_address(),
            phone_number = self.phone_number(),
            )

    def user(self):
        return users.User(self.email())

    def chance(self):
        return random.randint(1, 100) <= 50

    def integer(self):
        return random.randint(1, 1000000)

    def float(self):
        return random.triangular(1, 10000)

    def now(self):
        return datetime.datetime.now()

    def today(self):
        return datetime.date.today()

    def timestamp(self):
        return datetime.datetime.now().time()

    def key(self):
        return ndb.Key('Model', random.randint(1, 100000))

# --------------------------------------------------------------------
# Model
# --------------------------------------------------------------------

class Model(ndb.Model):

    def __init__(self, *args, **kwds):
        self._faker = Faker()
        super(Model, self).__init__(*args, **kwds)

    @classmethod
    def create(cls, **values):
        entity = cls(**values)
        entity.put()
        return entity

    @classmethod
    def generate(cls, count):
        generator = (cls.create() for i in xrange(count))
        return [entity for entity in generator]

# --------------------------------------------------------------------
# Base Property
# --------------------------------------------------------------------

class Property(ndb.Property):

    def __init__(self, length=1, **kwargs):
        try:
            self._length = int(length)
        except (ValueError, TypeError):
            raise ValueError("length must be an integer received %r" % length)

        super(Property, self).__init__(**kwargs)

    def _get_fake_value(self, entity):
        raise NotImplementedError()

    def _prepare_for_put(self, entity):
        if not self._has_value(entity):
            value = self._get_user_value(entity)
            if not value:
                if self._repeated:
                    value = [self._get_fake_value(entity) for x in xrange(self._length)]
                else:
                    value = self._get_fake_value(entity)

            self._store_value(entity, value)

# --------------------------------------------------------------------
# Fake Property
# --------------------------------------------------------------------

class FakeProperty(Property):

    _fake = None

    def __init__(self, fake=None, **kwargs):
        if fake is not None:
            try:
                getattr(Faker, fake)
            except (TypeError, AttributeError):
                raise ValueError("fake must be a valid method of Faker class received %s" % str(fake))

            self._fake = fake

        super(FakeProperty, self).__init__(**kwargs)

    def _get_fake_value(self, entity):
        if self._fake:
            return getattr(entity._faker, self._fake)()

        try:
            return getattr(entity._faker, self._name)()
        except AttributeError:
            return self._get_fallback_value(entity)

    def _get_fallback_value(self, entity):
        raise NotImplementedError()

# --------------------------------------------------------------------
# Integer Property
# --------------------------------------------------------------------

class IntegerProperty(FakeProperty, ndb.IntegerProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.integer()

# --------------------------------------------------------------------
# Float Property
# --------------------------------------------------------------------

class FloatProperty(FakeProperty, ndb.FloatProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.float()

# --------------------------------------------------------------------
# Boolean Property
# --------------------------------------------------------------------

class BooleanProperty(FakeProperty, ndb.BooleanProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.chance()

# --------------------------------------------------------------------
# Text Property
# --------------------------------------------------------------------

class TextProperty(FakeProperty, ndb.TextProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.lorem()

# --------------------------------------------------------------------
# String Property
# --------------------------------------------------------------------

class StringProperty(FakeProperty, ndb.StringProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.caption()

# --------------------------------------------------------------------
# Generic Property
# --------------------------------------------------------------------

class GenericProperty(FakeProperty, ndb.GenericProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.caption()

# --------------------------------------------------------------------
# Datetime Property
# --------------------------------------------------------------------

class DateTimeProperty(FakeProperty, ndb.DateTimeProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.now()

# --------------------------------------------------------------------
# Date Property
# --------------------------------------------------------------------

class DateProperty(FakeProperty, ndb.DateProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.today()

# --------------------------------------------------------------------
# Time Property
# --------------------------------------------------------------------

class TimeProperty(FakeProperty, ndb.TimeProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.timestamp()

# --------------------------------------------------------------------
# GeoPt Property
# --------------------------------------------------------------------

class GeoPtProperty(FakeProperty, ndb.GeoPtProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.coordinates()

# --------------------------------------------------------------------
# Key Property
# --------------------------------------------------------------------

class KeyProperty(FakeProperty, ndb.KeyProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.key()

# --------------------------------------------------------------------
# User Property
# --------------------------------------------------------------------

class UserProperty(FakeProperty, ndb.UserProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.user()

# --------------------------------------------------------------------
# Json Property
# --------------------------------------------------------------------

class JsonProperty(FakeProperty, ndb.JsonProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.profile()

# --------------------------------------------------------------------
# Pickle Property
# --------------------------------------------------------------------

class PickleProperty(FakeProperty, ndb.PickleProperty):

    def _get_fallback_value(self, entity):
        return entity._faker.profile()

# --------------------------------------------------------------------
# Computed Property
# --------------------------------------------------------------------

class ComputedProperty(ndb.ComputedProperty):
    pass

# --------------------------------------------------------------------
# Structured Property
# --------------------------------------------------------------------

class StructuredProperty(ndb.StructuredProperty):
    pass

# --------------------------------------------------------------------
# Local Structured Property
# --------------------------------------------------------------------

class LocalStructuredProperty(ndb.LocalStructuredProperty):
    pass

# --------------------------------------------------------------------
# Blob Property
# --------------------------------------------------------------------

class BlobProperty(ndb.BlobProperty):

    def __init__(self, **kwargs):
        raise NotImplementedError()
        super(BlobProperty, self).__init__(**kwargs)

# --------------------------------------------------------------------
# Blob Key Property
# --------------------------------------------------------------------

class BlobKeyProperty(ndb.BlobKeyProperty):

    def __init__(self, **kwargs):
        raise NotImplementedError()
        super(BlobKeyProperty, self).__init__(**kwargs)
