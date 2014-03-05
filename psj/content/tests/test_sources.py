# -*- coding: utf-8 -*-
# Tests for sources module.
import os
import shutil
import tempfile
import unittest
from plone.testing.zca import pushGlobalRegistry, popGlobalRegistry
from zope.component import getGlobalSiteManager
from zope.interface import verify
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from psj.content.interfaces import IExternalVocabConfig
from psj.content.sources import (
    ExternalVocabBinder, institutes_source, make_terms,
    )


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


class SourcesUnitTests(unittest.TestCase):

    def setUp(self):
        pushGlobalRegistry()
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        popGlobalRegistry()
        shutil.rmtree(self.workdir)

    def create_external_vocab(self, name, valid_path=True):
        # create a working external vocab and register it
        gsm = getGlobalSiteManager()
        path = os.path.join(self.workdir, 'sample_vocab.csv')
        if valid_path:
            open(path, 'w').write(
                u'Vocab Entry 1\nVocab Entry 2\nÜmlaut Entry\n'.encode(
                    'utf-8'))
        conf = {'path': path, 'name': name}
        gsm.registerUtility(conf, provided=IExternalVocabConfig, name=name)

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
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
