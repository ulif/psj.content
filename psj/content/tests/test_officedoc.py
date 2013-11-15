# Tests for officedoc module.
import unittest
from plone.app.testing import TEST_USER_ID, setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobFile
from zope.component import queryUtility, createObject
from zope.interface import verify
from psj.content.officedoc import IOfficeDoc, OfficeDoc
from psj.content.testing import INTEGRATION_TESTING

class OfficeDocUnitTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill all interface contracts
        obj = OfficeDoc()
        verify.verifyClass(IOfficeDoc, OfficeDoc)
        verify.verifyObject(IOfficeDoc, obj)


class OfficeDocIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.src_file = NamedBlobFile(
            data='Hi there!', filename=u'sample.txt')

    def test_adding(self):
        # we can add OfficeDoc instances
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1',
            psj_office_doc = self.src_file,
            )
        d1 = self.folder['doc1']
        self.assertTrue(IOfficeDoc.providedBy(d1))
        # additional attributes were set
        self.assertEqual(d1.psj_md5, '396199333edbf40ad43e62a1c1397793')
        assert d1.psj_html_repr.data is not None
        assert d1.psj_pdf_repr.data is not None

    def test_fti(self):
        # we can get factory type infos for officedocs
        fti = queryUtility(IDexterityFTI, name='psj.content.officedoc')
        assert fti is not None

    def test_schema(self):
        # our fti provides the correct schema
        fti = queryUtility(IDexterityFTI, name='psj.content.officedoc')
        schema = fti.lookupSchema()
        self.assertEqual(IOfficeDoc, schema)

    def test_factory(self):
        # our fti provides a factory for OfficeDoc instances
        fti = queryUtility(IDexterityFTI, name='psj.content.officedoc')
        factory = fti.factory
        new_obj = createObject(factory)
        self.assertTrue(IOfficeDoc.providedBy(new_obj))
