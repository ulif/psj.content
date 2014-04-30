# -*- coding: utf-8 -*-
# Tests for sources module.
import redis
import unittest
from testing.redis import RedisServer
from zope.interface import verify
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from psj.content.sources import (
    ExternalVocabBinder, RedisSource, make_terms,
    institutes_source, licenses_source, publishers_source,
    subjectgroup_source, ddcgeo_source, ddcsach_source, ddczeit_source,
    gndid_source,
    )
from psj.content.testing import ExternalVocabSetup


class MakeTermsTests(unittest.TestCase):
    # tests for the make_terms function

    def test_make_terms(self):
        result = make_terms(['foo', 'bar', 'baz'])
        for term in result:
            assert isinstance(term, SimpleTerm)
        assert len(result) == 3
        term_strings = [(x.title, x.token, x.value) for x in result]
        self.assertEqual(
            term_strings,
            [(u'foo', 'Zm9v', u'foo'),
             (u'bar', 'YmFy', u'bar'),
             (u'baz', 'YmF6', u'baz')]
            )

    def test_make_terms_umlauts(self):
        result = make_terms(['ümläut', 'ömläut'])
        term_strings = [(x.title, x.token, x.value) for x in result]
        self.assertEqual(
            term_strings,
            [(u'\xfcml\xe4ut', 'w7xtbMOkdXQ=', u'\xfcml\xe4ut'),
             (u'\xf6ml\xe4ut', 'w7ZtbMOkdXQ=', u'\xf6ml\xe4ut')]
            )

    def test_make_terms_ignore_empty(self):
        # emtpy strings are ignored when creating terms
        result = make_terms(['', 'foo', '', 'bar', ''])
        term_strings = [(x.title, x.token, x.value) for x in result]
        self.assertEqual(
            term_strings,
            [(u'foo', 'Zm9v', u'foo'),
             (u'bar', 'YmFy', u'bar')]
            )


class RedisSourceTests(unittest.TestCase):

    def setUp(self):
        self.redis_server = RedisServer()
        settings = self.redis_server.settings['redis_conf']
        port = settings['port']
        self.redis = redis.StrictRedis(host='localhost', port=port, db=0)
        self.redis.flushdb()
        self.redis.set(u'foo', u'bar')
        self.redis_host = settings['bind']
        self.redis_port = settings['port']

    def tearDown(self):
        self.redis.flushdb()
        self.redis.connection_pool.disconnect()
        self.redis_server.stop()

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


class SourcesUnitTests(ExternalVocabSetup, unittest.TestCase):

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
