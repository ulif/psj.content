# -*- coding: utf-8 -*-
# Tests for sources module.
import unittest
from zope.component import getGlobalSiteManager
from zope.interface import verify
from zope.schema.interfaces import (
    IContextSourceBinder, IVocabularyFactory,
    )
from zope.schema.vocabulary import SimpleVocabulary
from psj.content.sources import InstitutesSourceBinder, institutes_source
from psj.content.testing import SampleVocabFactory


class SourcesUnitTests(unittest.TestCase):

    def _unregister(self):
        gsm = getGlobalSiteManager()
        for name in [u'psj.content.Institutes', ]:
            gsm.unregisterUtility(name=name, provided=IVocabularyFactory)

    def setUp(self):
        self._unregister()

    def tearDown(self):
        self._unregister()

    def test_inst_src_binder_iface(self):
        binder = InstitutesSourceBinder()
        verify.verifyClass(IContextSourceBinder, InstitutesSourceBinder)
        verify.verifyObject(IContextSourceBinder, binder)

    def test_inst_src_wo_vocab(self):
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert 'one' not in src

    def test_inst_src_w_vocab(self):
        factory = SampleVocabFactory()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory, provided=IVocabularyFactory,
                            name=u'psj.content.Institutes')
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert 'one' in src
