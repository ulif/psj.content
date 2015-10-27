# -*- coding: utf-8 -*-
# Tests for sources module.
import redis
import unittest
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import verify
from zope.schema.interfaces import (
    IContextSourceBinder, IBaseVocabulary, ITitledTokenizedTerm,
    IIterableVocabulary, IVocabularyTokenized
    )
from zope.schema.vocabulary import SimpleVocabulary
from psj.content.sources import (
    ExternalVocabBinder, ExternalRedisBinder, RedisSource,
    RedisAutocompleteSource, RedisKeysSource, institutes_source,
    licenses_source, publishers_source,
    subjectgroup_source, ddcgeo_source, ddcsach_source, ddczeit_source,
    gndid_source,
    )
from psj.content.testing import ExternalVocabSetup, RedisLayer
from psj.content.utils import tokenize


class RedisSourceTests(unittest.TestCase):

    layer = RedisLayer

    def setUp(self):
        settings = self.layer['redis_server'].settings['redis_conf']
        port = settings['port']
        self.redis = redis.StrictRedis(host='localhost', port=port, db=0)
        self.redis.flushdb()
        self.redis.set(u'foo', u'bar')
        self.redis_host = settings['bind']
        self.redis_port = settings['port']

    def tearDown(self):
        self.redis.flushdb()

    def test_iface(self):
        # make sure we fullfill promised interfaces
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        verify.verifyClass(IQuerySource, RedisSource)
        verify.verifyObject(IQuerySource, source)

    def test_basic(self):
        # make sure, basic redis store test setup works
        r = self.redis
        result = r.get('foo')
        self.assertEqual(result, 'bar')

    def test_get_contained(self):
        # we can tell whether a certain key is stored in redis store
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        result = u'foo' in source
        self.assertEqual(result, True)

    def test_get_uncontained(self):
        # we can tell if a certain key is not in redis store
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        result = u'bar' in source
        self.assertEqual(result, False)

    def test_get_term_contained(self):
        # we can get contained terms as ITerm
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        term = source.getTerm(u'foo')
        assert ITitledTokenizedTerm.providedBy(term)
        self.assertTrue(hasattr(term, 'value'))
        self.assertEqual(term.value, u'foo')
        self.assertTrue(hasattr(term, 'token'))
        self.assertEqual(term.token, 'Zm9v')
        self.assertTrue(hasattr(term, 'title'))
        self.assertEqual(term.title, u'bar')

    def test_len(self):
        # we can get the size of a database
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        self.assertEqual(len(source), 1)
        self.redis.set("bar", "baz")
        self.assertEqual(len(source), 2)

    def test_iter(self):
        # we can iterate over all elements
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        elem_list = [x for x in source]
        self.assertEqual(len(elem_list), 1)
        self.assertTrue(ITitledTokenizedTerm.providedBy(elem_list[0]))

    def test_get_term_by_token(self):
        # we can get a term by its token
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        token = tokenize("foo")
        result = source.getTermByToken(token)
        self.assertTrue(ITitledTokenizedTerm.providedBy(result))

    def test_search(self):
        # we can search a source
        source = RedisSource(host=self.redis_host, port=self.redis_port)
        self.redis.set("far", "boo")
        self.redis.set("gaz", "hor")
        result1 = [x.title for x in source.search("b")]
        result2 = [x.title for x in source.search("h")]
        result3 = [x.title for x in source.search("ba")]
        self.assertEqual(sorted(result1), ["bar", "boo"])
        self.assertEqual(result2, ["hor"])
        self.assertEqual(result3, ["bar"])


class RedisKeysSourceTests(unittest.TestCase):

    layer = RedisLayer

    def setUp(self):
        settings = self.layer['redis_server'].settings['redis_conf']
        port = settings['port']
        self.redis = redis.StrictRedis(host='localhost', port=port, db=0)
        self.redis.flushdb()
        self.redis.set(u'foo', u'bar')
        self.redis_host = settings['bind']
        self.redis_port = settings['port']

    def tearDown(self):
        self.redis.flushdb()

    def test_iface(self):
        # make sure we fullfill promised interfaces
        source = RedisKeysSource(host=self.redis_host, port=self.redis_port)
        verify.verifyClass(IQuerySource, RedisKeysSource)
        verify.verifyObject(IQuerySource, source)

    def test_get_contained(self):
        # we can tell whether a certain key is stored in redis store
        source = RedisKeysSource(host=self.redis_host, port=self.redis_port)
        result = u'foo' in source
        self.assertEqual(result, True)

    def test_get_uncontained(self):
        # we can tell if a certain key is not in redis store
        source = RedisKeysSource(host=self.redis_host, port=self.redis_port)
        result = u'bar' in source
        self.assertEqual(result, False)

    def test_get_term_contained(self):
        # we can get contained terms as ITerm
        source = RedisKeysSource(host=self.redis_host, port=self.redis_port)
        term = source.getTerm(u'foo')
        assert ITitledTokenizedTerm.providedBy(term)
        self.assertTrue(hasattr(term, 'value'))
        self.assertEqual(term.value, u'foo')
        self.assertTrue(hasattr(term, 'token'))
        self.assertEqual(term.token, 'Zm9v')
        self.assertTrue(hasattr(term, 'title'))
        self.assertEqual(term.title, u'foo')


class RedisAutocompleteSourceTests(unittest.TestCase):

    layer = RedisLayer

    def setUp(self):
        settings = self.layer['redis_server'].settings['redis_conf']
        port = settings['port']
        self.redis = redis.StrictRedis(host='localhost', port=port, db=0)
        self.redis.flushdb()
        self.redis.zadd(u'autocomplete-foo', 0, "foo (1)&&Foo (1)")
        self.redis.zadd(u'autocomplete-foo', 0, "for (2)&&For (2)")
        self.redis.zadd(u'autocomplete-foo', 0, "baz (3)&&Baz (3)")
        self.redis.zadd(u'autocomplete-foo', 0, "bar (4)&&Bar (4)")
        self.redis_host = settings['bind']
        self.redis_port = settings['port']

    def tearDown(self):
        self.redis.flushdb()

    def test_iface(self):
        # make sure we fullfill promised interfaces
        source = RedisAutocompleteSource(
            host=self.redis_host, port=self.redis_port)
        verify.verifyClass(IQuerySource, RedisAutocompleteSource)
        verify.verifyObject(IQuerySource, source)

    def test_get_contained(self):
        # we can tell whether a certain key is stored in redis store
        source = RedisAutocompleteSource(
            host=self.redis_host, port=self.redis_port,
            zset_name="autocomplete-foo")
        result = u'foo (1)' in source
        self.assertEqual(result, True)

    def test_get_uncontained(self):
        # we can tell if a certain key is not in redis store
        source = RedisAutocompleteSource(
            host=self.redis_host, port=self.redis_port,
            zset_name="autocomplete-foo")
        result = u'bar' in source
        self.assertEqual(result, False)


class ExternalVocabBinderTests(ExternalVocabSetup, unittest.TestCase):

    def test_external_vocab_binder_iface(self):
        binder = ExternalVocabBinder(None)
        verify.verifyClass(IContextSourceBinder, ExternalVocabBinder)
        verify.verifyObject(IContextSourceBinder, binder)

    def test_external_vocab_binder_no_conf(self):
        # we cope with not registered utils
        binder = ExternalVocabBinder(name='not-a-registered-util-name')
        vocab = binder(context=None)
        assert isinstance(vocab, SimpleVocabulary)
        assert len([x for x in vocab]) == 0

    def test_external_vocab_binder_no_valid_path(self):
        # we cope with external confs where path is invalid
        self.create_external_vocab('psj.content.testvocab', valid_path=False)
        binder = ExternalVocabBinder(name='psj.content.testvocab')
        vocab = binder(context=None)
        assert isinstance(vocab, SimpleVocabulary)
        assert len([x for x in vocab]) == 0

    def test_inst_src_w_vocab(self):
        self.create_external_vocab('psj.content.Institutes')
        institutes_source.vocab = None  # make sure not to get cached entries
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_licenses_src_w_vocab(self):
        self.create_external_vocab('psj.content.Licenses')
        licenses_source.vocab = None  # make sure not to get cached entries
        src = licenses_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_publishers_src_w_vocab(self):
        self.create_external_vocab('psj.content.Publishers')
        publishers_source.vocab = None  # make sure not to get cached entries
        src = publishers_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_subjectgroup_src_w_vocab(self):
        self.create_external_vocab('psj.content.Subjectgroup')
        subjectgroup_source.vocab = None  # avoid cached entries
        src = subjectgroup_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_ddcgeo_src_w_vocab(self):
        self.create_external_vocab('psj.content.DDCGeo')
        ddcgeo_source.vocab = None  # avoid cached entries
        src = ddcgeo_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_ddcsach_src_w_vocab(self):
        self.create_external_vocab('psj.content.DDCSach')
        ddcsach_source.vocab = None  # avoid cached entries
        src = ddcsach_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_ddczeit_src_w_vocab(self):
        self.create_external_vocab('psj.content.DDCZeit')
        ddczeit_source.vocab = None  # avoid cached entries
        src = ddczeit_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src

    def test_gndid_src_w_vocab(self):
        self.create_external_vocab('psj.content.GND_ID')
        gndid_source.vocab = None  # avoid cached entries
        src = gndid_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert u'Vocab Entry 1' in src


class ExternalRedisBinderTests(unittest.TestCase):

    layer = RedisLayer

    def setUp(self):
        settings = self.layer['redis_server'].settings['redis_conf']
        port = settings['port']
        self.redis = redis.StrictRedis(host='localhost', port=port, db=0)
        self.redis.flushdb()
        self.redis.set(u'foo', u'bar')
        self.redis.set(u'bar', u'baz')
        self.redis_host = settings['bind']
        self.redis_port = settings['port']

    def tearDown(self):
        self.redis.flushdb()

    def register_redis_conf(self, name='my-conf', invalid=0):
        # register a redis config as a named utility
        from zope.component import getGlobalSiteManager
        from psj.content.interfaces import IRedisStoreConfig
        gsm = getGlobalSiteManager()
        conf = {
            'host': self.redis_host,
            'port': self.redis_port,
            'db': 0 + invalid
            }
        gsm.registerUtility(conf, provided=IRedisStoreConfig, name=name)

    def test_external_redis_binder_iface(self):
        binder = ExternalRedisBinder(None)
        verify.verifyClass(IContextSourceBinder, ExternalRedisBinder)
        verify.verifyObject(IContextSourceBinder, binder)

    def test_external_redis_binder_no_conf(self):
        # we cope with not registered redis confs
        binder = ExternalRedisBinder(name='not-a-registered-util-name')
        vocab = binder(context=None)
        assert isinstance(vocab, SimpleVocabulary)
        assert len([x for x in vocab]) == 0

    def test_external_redis_binder_invalid_conf(self):
        # with an invalid redis conf, we get empty sources
        self.register_redis_conf(name='my-test-redis-conf', invalid=1)
        binder = ExternalRedisBinder(name='my-test-redis-conf')
        source = binder(context=None)
        self.assertRaises(LookupError, source.getTerm, u'foo')
        assert isinstance(source, RedisSource)
        assert u'foo' not in source

    def test_external_redis_binder_valid_conf(self):
        # with a valid redis conf, we get valid vocabs
        self.register_redis_conf(name='my-test-redis-conf')
        binder = ExternalRedisBinder(name='my-test-redis-conf')
        source = binder(context=None)
        term = source.getTerm(u'foo')
        assert isinstance(source, RedisSource)
        assert u'foo' in source
        assert u'bar' in source
        assert u'baz' not in source
        self.assertEqual(term.value, u'foo')
        self.assertEqual(term.title, u'bar')
