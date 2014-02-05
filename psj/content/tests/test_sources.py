# -*- coding: utf-8 -*-
# Tests for sources module.
import unittest
from five import grok
from plone.app.testing import (
    TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, setRoles,
    )
from psj.content.testing import INTEGRATION_TESTING
from zope.component import getGlobalSiteManager
from zope.interface import verify
from zope.schema.interfaces import (
    IContextSourceBinder, ISource, IVocabularyFactory,
    )
from zope.schema.vocabulary import SimpleVocabulary
from psj.content.sources import institutes_source


@grok.implementer(IVocabularyFactory)
class SampleVocabFactory(object):
    def __call__(self):
        return SimpleVocabulary.fromValues(['one', 'two', 'three'])


class SourcesUnitTests(unittest.TestCase):

    def _unregister(self):
        gsm = getGlobalSiteManager()
        for name in [u'psj.content.Institutes', ]:
            gsm.unregisterUtility(name=name, provided=IVocabularyFactory)

    def setUp(self):
        self._unregister()

    def tearDown(self):
        self._unregister()

    def test_inst_src_iface(self):
        src = institutes_source(None)
        verify.verifyClass(IContextSourceBinder, institutes_source)
        verify.verifyObject(IContextSourceBinder, src)

    def test_inst_src_wo_vocab(self):
        src = institutes_source(None)
        assert isinstance(src(None), SimpleVocabulary)
        assert 'one' not in src(None)

    def test_inst_src_w_vocab(self):
        factory = SampleVocabFactory()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory, provided=IVocabularyFactory,
                            name=u'psj.content.Institutes')
        src = institutes_source(None)(None)
        assert isinstance(src, SimpleVocabulary)
        assert 'one' in src
