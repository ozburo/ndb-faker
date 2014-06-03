# -*- coding: utf-8 -*-
"""
tests.py

"""

import os
import sys
import logging
import unittest

sys.path.insert(0, '/usr/local/google_appengine')

import dev_appserver
dev_appserver.fix_sys_path()

from google.appengine.ext import testbed
from google.appengine.ext import ndb

from google.appengine.datastore import datastore_stub_util

from google.appengine.api import users

from ndb_faker import model, fake

import datetime
import webapp2

# --------------------------------------------------------------------
# Base Test Case
# --------------------------------------------------------------------

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the test framework.

        Service stubs are available for the following services:

        - Datastore (use init_datastore_v3_stub)
        - Memcache (use init_memcache_stub)
        - Task Queue (use init_taskqueue_stub)
        - Images (only for dev_appserver; use init_images_stub)
        - URL fetch (use init_urlfetch_stub)
        - User service (use init_user_stub)
        - XMPP (use init_xmpp_stub)
        """
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        # To set custom env vars, pass them as kwargs *after* activate().
        # self.setup_env()

        # Next, declare which service stubs you want to use.
        # self.testbed.init_memcache_stub()
        # self.testbed.init_user_stub()

        # Add taskqueue support with our queue.yaml path
        # self.testbed.init_taskqueue_stub(root_path=os.path.dirname(os.path.dirname( __file__ )))

        # Create a consistency policy that will simulate the High Replication consistency model.
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=0)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy, require_indexes=False)
        # self.testbed.init_datastore_v3_stub(consistency_policy=self.policy, require_indexes=True,
        #                                     root_path=os.path.dirname(os.path.dirname( __file__ )))

        # Only when testing ndb.
        self.reset_kind_map()
        self.setup_context_cache()

    def tearDown(self):
        # This restores the original stubs so that tests do not interfere
        # with each other.
        self.testbed.deactivate()
        # Clear thread-local variables.
        self.clear_globals()

    def reset_kind_map(self):
        ndb.model.Model._reset_kind_map()

    def setup_context_cache(self):
        """Set up the context cache.

        We only need cache active when testing the cache, so the default
        behavior is to disable it to avoid misleading test results. Override
        this when needed.
        """
        ctx = ndb.tasklets.get_context()
        ctx.set_cache_policy(False)
        ctx.set_memcache_policy(False)

    def clear_globals(self):
        webapp2._local.__release_local__()

    def register_model(self, name, cls):
        ndb.model.Model._kind_map[name] = cls

# --------------------------------------------------------------------
# Fake Test Case
# --------------------------------------------------------------------

class FakeTestCase(BaseTestCase):

    #
    # Imports
    # ----------------------------------------------------------------

    def test_imports(self):
        model.Model
        model.IntegerProperty
        model.FloatProperty
        model.BooleanProperty
        model.StringProperty
        model.TextProperty
        model.BlobProperty
        model.DateTimeProperty
        model.DateProperty
        model.TimeProperty
        model.GeoPtProperty
        model.KeyProperty
        model.BlobKeyProperty
        model.UserProperty
        model.StructuredProperty
        model.LocalStructuredProperty
        model.JsonProperty
        model.PickleProperty
        model.GenericProperty
        model.ComputedProperty

        fake.Model
        fake.IntegerProperty
        fake.FloatProperty
        fake.BooleanProperty
        fake.StringProperty
        fake.TextProperty
        fake.BlobProperty
        fake.DateTimeProperty
        fake.DateProperty
        fake.TimeProperty
        fake.GeoPtProperty
        fake.KeyProperty
        fake.BlobKeyProperty
        fake.UserProperty
        fake.StructuredProperty
        fake.LocalStructuredProperty
        fake.JsonProperty
        fake.PickleProperty
        fake.GenericProperty
        fake.ComputedProperty

    #
    # Model
    # ----------------------------------------------------------------

    def test_model_create(self):
        class Model(model.Model):
            name = model.StringProperty()
        entity = Model.create()
        entity._faker

        entity = Model.create(name='john')
        self.assertEqual(entity.name, 'john')

    def test_model_generate(self):
        class Model(model.Model):
            pass

        entities = Model.generate(12)
        self.assertEqual(len(entities), 12)

    def test_model_faker_memoization(self):
        class Model(model.Model):
            pass

        entity = Model()

        first_name = entity._faker.first_name()
        last_name = entity._faker.last_name()
        username = entity._faker.username()
        email = entity._faker.email()
        name = entity._faker.name()

        self.assertIn(first_name, name)
        self.assertIn(last_name, name)
        self.assertIn(username, email)

    #
    # Property
    # ----------------------------------------------------------------

    def test_property_length(self):
        self.assertRaises(ValueError, model.Property, length=None)
        self.assertRaises(ValueError, model.Property, length='#badint')

    def test_property_fake(self):
        self.assertRaises(ValueError, model.FakeProperty, fake='notmethod')
        self.assertRaises(ValueError, model.FakeProperty, fake=123)
        self.assertRaises(ValueError, model.FakeProperty, fake=(123))

    #
    # Integer Property
    # ----------------------------------------------------------------

    def test_integer_property_value(self):
        class Model(model.Model):
            prop = model.IntegerProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, int)

    def test_integer_property_value_fake(self):
        class Model(model.Model):
            prop = model.IntegerProperty(fake='age')
        entity = Model.create()

        self.assertIsInstance(entity.prop, int)

    def test_integer_property_value_prop(self):
        class Model(model.Model):
            age = model.IntegerProperty()
        entity = Model.create()

        self.assertIsInstance(entity.age, int)

    def test_integer_property_required(self):
        class Model(model.Model):
            prop = model.IntegerProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, int)

    def test_integer_property_default(self):
        class Model(model.Model):
            prop = model.IntegerProperty(default=1)
        entity = Model.create()

        self.assertIsInstance(entity.prop, int)
        self.assertEqual(entity.prop, 1)

    def test_integer_property_repeated_default(self):
        self.assertRaises(ValueError, model.IntegerProperty, default=1, repeated=True)

    def test_integer_property_repeated_value(self):
        class Model(model.Model):
            prop = model.IntegerProperty(fake='age', repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_integer_property_repeated_length(self):
        class Model(model.Model):
            prop = model.IntegerProperty(fake='age', length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Float Property
    # ----------------------------------------------------------------

    def test_float_property_value(self):
        class Model(model.Model):
            prop = model.FloatProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, float)

    def test_float_property_value_fake(self):
        class Model(model.Model):
            prop = model.FloatProperty(fake='latitude')
        entity = Model.create()

        self.assertIsInstance(entity.prop, float)

    def test_float_property_value_prop(self):
        class Model(model.Model):
            age = model.FloatProperty()
        entity = Model.create()

        self.assertIsInstance(entity.age, float)

    def test_float_property_required(self):
        class Model(model.Model):
            prop = model.FloatProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, float)

    def test_float_property_default(self):
        class Model(model.Model):
            prop = model.FloatProperty(default=1)
        entity = Model.create()

        self.assertIsInstance(entity.prop, float)
        self.assertEqual(entity.prop, 1)

    def test_float_property_repeated_default(self):
        self.assertRaises(ValueError, model.FloatProperty, default=1, repeated=True)

    def test_float_property_repeated_value(self):
        class Model(model.Model):
            prop = model.FloatProperty(fake='longitude', repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_float_property_repeated_length(self):
        class Model(model.Model):
            prop = model.FloatProperty(fake='age', length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Boolean Property
    # ----------------------------------------------------------------

    def test_boolean_property_value(self):
        class Model(model.Model):
            prop = model.BooleanProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, bool)

    def test_boolean_property_value_fake(self):
        class Model(model.Model):
            prop = model.BooleanProperty(fake='chance')
        entity = Model.create()

        self.assertIsInstance(entity.prop, bool)

    def test_boolean_property_value_prop(self):
        class Model(model.Model):
            chance = model.BooleanProperty()
        entity = Model.create()

        self.assertIsInstance(entity.chance, bool)

    def test_boolean_property_required(self):
        class Model(model.Model):
            prop = model.BooleanProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, bool)

    def test_boolean_property_default(self):
        class Model(model.Model):
            prop = model.BooleanProperty(default=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, bool)
        self.assertEqual(entity.prop, True)

    def test_boolean_property_repeated_default(self):
        self.assertRaises(ValueError, model.BooleanProperty, default=1, repeated=True)

    def test_boolean_property_repeated_value(self):
        class Model(model.Model):
            prop = model.BooleanProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_boolean_property_repeated_length(self):
        class Model(model.Model):
            prop = model.BooleanProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # String Property
    # ----------------------------------------------------------------

    def test_string_property_value(self):
        class Model(model.Model):
            prop = model.StringProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_string_property_value_fake(self):
        class Model(model.Model):
            prop = model.StringProperty(fake='first_name')
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_string_property_value_prop(self):
        class Model(model.Model):
            username = model.StringProperty()
        entity = Model.create()

        self.assertIsInstance(entity.username, basestring)

    def test_string_property_required(self):
        class Model(model.Model):
            prop = model.StringProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_string_property_default(self):
        class Model(model.Model):
            prop = model.StringProperty(default='abc')
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)
        self.assertEqual(entity.prop, 'abc')

    def test_string_property_repeated_default(self):
        self.assertRaises(ValueError, model.StringProperty, default=1, repeated=True)

    def test_string_property_repeated_value(self):
        class Model(model.Model):
            prop = model.StringProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_string_property_repeated_length(self):
        class Model(model.Model):
            prop = model.StringProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Text Property
    # ----------------------------------------------------------------

    def test_text_property_value(self):
        class Model(model.Model):
            prop = model.TextProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_text_property_value_fake(self):
        class Model(model.Model):
            prop = model.TextProperty(fake='first_name')
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_text_property_value_prop(self):
        class Model(model.Model):
            username = model.TextProperty()
        entity = Model.create()

        self.assertIsInstance(entity.username, basestring)

    def test_text_property_required(self):
        class Model(model.Model):
            prop = model.TextProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_text_property_default(self):
        class Model(model.Model):
            prop = model.TextProperty(default='abc')
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)
        self.assertEqual(entity.prop, 'abc')

    def test_text_property_repeated_default(self):
        self.assertRaises(ValueError, model.TextProperty, default=1, repeated=True)

    def test_text_property_repeated_value(self):
        class Model(model.Model):
            prop = model.TextProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_text_property_repeated_length(self):
        class Model(model.Model):
            prop = model.TextProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Generic Property
    # ----------------------------------------------------------------

    def test_generic_property_value(self):
        class Model(model.Model):
            prop = model.GenericProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_generic_property_value_fake(self):
        class Model(model.Model):
            prop = model.GenericProperty(fake='age')
        entity = Model.create()

        self.assertIsInstance(entity.prop, int)

    def test_generic_property_value_prop(self):
        class Model(model.Model):
            username = model.GenericProperty()
        entity = Model.create()

        self.assertIsInstance(entity.username, basestring)

    def test_generic_property_required(self):
        class Model(model.Model):
            prop = model.GenericProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)

    def test_generic_property_default(self):
        class Model(model.Model):
            prop = model.GenericProperty(default='abc')
        entity = Model.create()

        self.assertIsInstance(entity.prop, basestring)
        self.assertEqual(entity.prop, 'abc')

    def test_generic_property_repeated_default(self):
        self.assertRaises(ValueError, model.GenericProperty, default=1, repeated=True)

    def test_generic_property_repeated_value(self):
        class Model(model.Model):
            prop = model.GenericProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_generic_property_repeated_length(self):
        class Model(model.Model):
            prop = model.GenericProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # DateTime Property
    # ----------------------------------------------------------------

    def test_datetime_property_value(self):
        class Model(model.Model):
            prop = model.DateTimeProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.datetime)

    def test_datetime_property_value_fake(self):
        class Model(model.Model):
            prop = model.DateTimeProperty(fake='now')
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.datetime)

    def test_datetime_property_value_prop(self):
        class Model(model.Model):
            now = model.DateTimeProperty()
        entity = Model.create()

        self.assertIsInstance(entity.now, datetime.datetime)

    def test_datetime_property_required(self):
        class Model(model.Model):
            prop = model.DateTimeProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.datetime)

    def test_datetime_property_default(self):
        now = datetime.datetime.now()
        class Model(model.Model):
            prop = model.DateTimeProperty(default=now)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.datetime)
        self.assertEqual(entity.prop, now)

    def test_datetime_property_repeated_default(self):
        self.assertRaises(ValueError, model.DateTimeProperty, default=1, repeated=True)

    def test_datetime_property_repeated_value(self):
        class Model(model.Model):
            prop = model.DateTimeProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_datetime_property_repeated_length(self):
        class Model(model.Model):
            prop = model.DateTimeProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Date Property
    # ----------------------------------------------------------------

    def test_date_property_value(self):
        class Model(model.Model):
            prop = model.DateProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.date)

    def test_date_property_value_fake(self):
        class Model(model.Model):
            prop = model.DateProperty(fake='today')
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.date)

    def test_date_property_value_prop(self):
        class Model(model.Model):
            today = model.DateProperty()
        entity = Model.create()

        self.assertIsInstance(entity.today, datetime.date)

    def test_date_property_required(self):
        class Model(model.Model):
            prop = model.DateProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.date)

    def test_date_property_default(self):
        now = datetime.date.today()
        class Model(model.Model):
            prop = model.DateProperty(default=now)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.date)
        self.assertEqual(entity.prop, now)

    def test_date_property_repeated_default(self):
        self.assertRaises(ValueError, model.DateProperty, default=1, repeated=True)

    def test_date_property_repeated_value(self):
        class Model(model.Model):
            prop = model.DateProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_date_property_repeated_length(self):
        class Model(model.Model):
            prop = model.DateProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Time Property
    # ----------------------------------------------------------------

    def test_time_property_value(self):
        class Model(model.Model):
            prop = model.TimeProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.time)

    def test_time_property_value_fake(self):
        class Model(model.Model):
            prop = model.TimeProperty(fake='timestamp')
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.time)

    def test_time_property_value_prop(self):
        class Model(model.Model):
            timestamp = model.TimeProperty()
        entity = Model.create()

        self.assertIsInstance(entity.timestamp, datetime.time)

    def test_time_property_required(self):
        class Model(model.Model):
            prop = model.TimeProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.time)

    def test_time_property_default(self):
        now = datetime.datetime.now().time()
        class Model(model.Model):
            prop = model.TimeProperty(default=now)
        entity = Model.create()

        self.assertIsInstance(entity.prop, datetime.time)
        self.assertEqual(entity.prop, now)

    def test_time_property_repeated_default(self):
        self.assertRaises(ValueError, model.TimeProperty, default=1, repeated=True)

    def test_time_property_repeated_value(self):
        class Model(model.Model):
            prop = model.TimeProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_time_property_repeated_length(self):
        class Model(model.Model):
            prop = model.TimeProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # User Property
    # ----------------------------------------------------------------

    def test_user_property_value(self):
        class Model(model.Model):
            prop = model.UserProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, users.User)
        self.assertIn('@', entity.prop.email())

    def test_user_property_memoization(self):
        class Model(model.Model):
            username = model.StringProperty()
            user = model.UserProperty()
        entity = Model.create()

        self.assertIn(entity.username, entity.user.email())

    def test_user_property_value_fake(self):
        class Model(model.Model):
            prop = model.UserProperty(fake='user')
        entity = Model.create()

        self.assertIsInstance(entity.prop, users.User)

    def test_user_property_value_prop(self):
        class Model(model.Model):
            user = model.UserProperty()
        entity = Model.create()

        self.assertIsInstance(entity.user, users.User)

    def test_user_property_required(self):
        class Model(model.Model):
            prop = model.UserProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, users.User)

    def test_user_property_default(self):
        class Model(model.Model):
            prop = model.UserProperty(default=users.User('test@example.com'))
        entity = Model.create()

        self.assertIsInstance(entity.prop, users.User)
        self.assertEqual(entity.prop, users.User('test@example.com'))

    def test_user_property_repeated_default(self):
        self.assertRaises(ValueError, model.UserProperty, default=1, repeated=True)

    def test_user_property_repeated_value(self):
        class Model(model.Model):
            prop = model.UserProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_user_property_repeated_length(self):
        class Model(model.Model):
            prop = model.UserProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # GeoPt Property
    # ----------------------------------------------------------------

    def test_geopt_property_value(self):
        class Model(model.Model):
            prop = model.GeoPtProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.GeoPt)

    def test_geopt_property_value_fake(self):
        class Model(model.Model):
            prop = model.GeoPtProperty(fake='coordinates')
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.GeoPt)

    def test_geopt_property_value_prop(self):
        class Model(model.Model):
            coordinates = model.GeoPtProperty()
        entity = Model.create()

        self.assertIsInstance(entity.coordinates, ndb.GeoPt)

    def test_geopt_property_required(self):
        class Model(model.Model):
            prop = model.GeoPtProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.GeoPt)

    def test_geopt_property_default(self):
        class Model(model.Model):
            prop = model.GeoPtProperty(default=ndb.GeoPt('54.12,-23.41'))
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.GeoPt)
        self.assertEqual(entity.prop, ndb.GeoPt('54.12,-23.41'))

    def test_geopt_property_repeated_default(self):
        self.assertRaises(ValueError, model.GeoPtProperty, default=1, repeated=True)

    def test_geopt_property_repeated_value(self):
        class Model(model.Model):
            prop = model.GeoPtProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_geopt_property_repeated_length(self):
        class Model(model.Model):
            prop = model.GeoPtProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Key Property
    # ----------------------------------------------------------------

    def test_key_property_value(self):
        class Model(model.Model):
            prop = model.KeyProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.Key)

    def test_key_property_value_fake(self):
        class Model(model.Model):
            prop = model.KeyProperty(fake='key')
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.Key)

    def test_key_property_value_prop(self):
        class Model(model.Model):
            key = model.KeyProperty()
        entity = Model.create()

        self.assertIsInstance(entity.key, ndb.Key)

    def test_key_property_required(self):
        class Model(model.Model):
            prop = model.KeyProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.Key)

    def test_key_property_default(self):
        class Model(model.Model):
            prop = model.KeyProperty(default=ndb.Key('Model', 1))
        entity = Model.create()

        self.assertIsInstance(entity.prop, ndb.Key)
        self.assertEqual(entity.prop, ndb.Key('Model', 1))

    def test_key_property_repeated_default(self):
        self.assertRaises(ValueError, model.KeyProperty, default=1, repeated=True)

    def test_key_property_repeated_value(self):
        class Model(model.Model):
            prop = model.KeyProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_key_property_repeated_length(self):
        class Model(model.Model):
            prop = model.KeyProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Json Property
    # ----------------------------------------------------------------

    def test_json_property_value(self):
        class Model(model.Model):
            prop = model.JsonProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_json_property_value_fake(self):
        class Model(model.Model):
            prop = model.JsonProperty(fake='profile')
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_json_property_value_prop(self):
        class Model(model.Model):
            profile = model.JsonProperty()
        entity = Model.create()

        self.assertIsInstance(entity.profile, dict)

    def test_json_property_required(self):
        class Model(model.Model):
            prop = model.JsonProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_json_property_default(self):
        class Model(model.Model):
            prop = model.JsonProperty(default={'name': "John"})
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)
        self.assertEqual(entity.prop, {'name': "John"})

    def test_json_property_repeated_default(self):
        self.assertRaises(ValueError, model.JsonProperty, default=1, repeated=True)

    def test_json_property_repeated_value(self):
        class Model(model.Model):
            prop = model.JsonProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_json_property_repeated_length(self):
        class Model(model.Model):
            prop = model.JsonProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Pickle Property
    # ----------------------------------------------------------------

    def test_pickle_property_value(self):
        class Model(model.Model):
            prop = model.PickleProperty()
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_pickle_property_value_fake(self):
        class Model(model.Model):
            prop = model.PickleProperty(fake='profile')
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_pickle_property_value_prop(self):
        class Model(model.Model):
            profile = model.PickleProperty()
        entity = Model.create()

        self.assertIsInstance(entity.profile, dict)

    def test_pickle_property_required(self):
        class Model(model.Model):
            prop = model.PickleProperty(required=True)
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)

    def test_pickle_property_default(self):
        class Model(model.Model):
            prop = model.PickleProperty(default={'name': "John"})
        entity = Model.create()

        self.assertIsInstance(entity.prop, dict)
        self.assertEqual(entity.prop, {'name': "John"})

    def test_pickle_property_repeated_default(self):
        self.assertRaises(ValueError, model.PickleProperty, default=1, repeated=True)

    def test_pickle_property_repeated_value(self):
        class Model(model.Model):
            prop = model.PickleProperty(repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 1)

    def test_pickle_property_repeated_length(self):
        class Model(model.Model):
            prop = model.PickleProperty(length=6, repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.prop), 6)

    #
    # Computed Property
    # ----------------------------------------------------------------

    def test_computed_property_value(self):
        class Model(model.Model):
            name = model.StringProperty()
            computed = model.ComputedProperty(lambda self: self.name.lower())
        entity = Model.create()

        self.assertEqual(entity.computed, entity.name.lower())

    def test_computed_property_repeated_value(self):
        class Model(model.Model):
            name = model.StringProperty(repeated=True, length=3)
            computed = model.ComputedProperty(lambda self: [n.lower() for n in self.name], repeated=True)
        entity = Model.create()

        self.assertEqual(len(entity.computed), 3)

    #
    # Structured Property
    # ----------------------------------------------------------------

    def test_structured_property_value(self):
        class InlineModel(model.Model):
            name = model.StringProperty()
            username = model.StringProperty()

        class Model(model.Model):
            structured = model.StructuredProperty(InlineModel, default=InlineModel())
        entity = Model.create()

        self.assertIsInstance(entity.structured.name, basestring)
        self.assertIsInstance(entity.structured.username, basestring)

    #
    # Local Structured Property
    # ----------------------------------------------------------------

    def test_local_structured_property_value(self):
        class InlineModel(model.Model):
            name = model.StringProperty()
            username = model.StringProperty()

        class Model(model.Model):
            structured = model.LocalStructuredProperty(InlineModel, default=InlineModel())
        entity = Model.create()

        self.assertIsInstance(entity.structured.name, basestring)
        self.assertIsInstance(entity.structured.username, basestring)

    #
    # Blob Property
    # ----------------------------------------------------------------

    def test_blob_property(self):
        self.assertRaises(NotImplementedError, model.BlobProperty)

    #
    # Blob Key Property
    # ----------------------------------------------------------------

    def test_blob_key_property(self):
        self.assertRaises(NotImplementedError, model.BlobKeyProperty)

    # ----------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
