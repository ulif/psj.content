# -*- coding: utf-8 -*-
# Tests for zcml module.
import os
import unittest
from zope.component import queryUtility
from zope.configuration import xmlconfig
from psj.content.interfaces import IExternalVocabConfig, IRedisStoreConfig


class ZCMLDirectiveTests(unittest.TestCase):

    def test_external_vocab_directive(self):
        # The local sample.zcml contain an external-vocab directive.
        sample_zcml = os.path.join(
            os.path.dirname(__file__), 'sample.zcml')
        xmlconfig.xmlconfig(open(sample_zcml, 'r'))
        conf1 = queryUtility(IExternalVocabConfig, name=u'psj.content.bar')
        conf2 = queryUtility(IExternalVocabConfig, name=u'psj.content.baz')
        conf3 = queryUtility(IExternalVocabConfig, name=u'psj.content.foo')
        self.assertEqual(
            conf1, {'path': u'/foo', 'name': u'psj.content.bar'})
        self.assertEqual(
            conf2, {'path': u'/bar', 'name': u'psj.content.baz'})
        self.assertTrue(conf3 is None)

    def test_redis_store_config(self):
        # The local sample.zcml contains a couple of redis store configs
        sample_zcml = os.path.join(
            os.path.dirname(__file__), 'sample.zcml')
        xmlconfig.xmlconfig(open(sample_zcml, 'r'))
        conf1 = queryUtility(IRedisStoreConfig, name=u'psj.content.redis-foo')
        conf2 = queryUtility(IRedisStoreConfig, name=u'psj.content.redis-bar')
        conf3 = queryUtility(IRedisStoreConfig, name=u'psj.content.redis-baz')
        self.assertEqual(
            conf1, {'host': 'localhost', 'port': 1234, 'db': 23})
        self.assertEqual(
            conf2, {'host': 'localhost', 'port': 6379, 'db': 0})
        self.assertEqual(
            conf3, {'host': 'localhost', 'port': 666, 'db': 0})
