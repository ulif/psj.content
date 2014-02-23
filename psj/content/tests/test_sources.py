# -*- coding: utf-8 -*-
# Tests for sources module.
import os
import shutil
import tempfile
import unittest
from zope.component import getGlobalSiteManager
from zope.interface import verify
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from psj.content.interfaces import IExternalVocabConfig
from psj.content.sources import InstitutesSourceBinder, institutes_source


class SourcesUnitTests(unittest.TestCase):

    def _unregister(self):
        gsm = getGlobalSiteManager()
        for name in [u'psj.content.Institutes', ]:
            gsm.unregisterUtility(name=name, provided=IExternalVocabConfig)

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self._unregister()

    def tearDown(self):
        self._unregister()
        shutil.rmtree(self.workdir)

    def create_working_external_vocab(self, name):
        # create a working external vocab and register it
        gsm = getGlobalSiteManager()
        path = os.path.join(self.workdir, 'sample_vocab.csv')
        open(path, 'w').write(
            u'Vocab Entry 1\nVocab Entry 2\nÜmlaut Entry\n'.encode('utf-8'))
        conf = {'path': path, 'name': name}
        gsm.registerUtility(conf, provided=IExternalVocabConfig, name=name)

    def test_inst_src_binder_iface(self):
        binder = InstitutesSourceBinder()
        verify.verifyClass(IContextSourceBinder, InstitutesSourceBinder)
        verify.verifyObject(IContextSourceBinder, binder)

    def test_inst_src_w_vocab(self):
        self.create_working_external_vocab('psj.content.Institutes')
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert "Vocab Entry 1" in src

    def test_inst_src_wo_vocab(self):
        src = institutes_source(context=None)
        assert isinstance(src, SimpleVocabulary)
        assert 'Vocab Entry 1' not in src
