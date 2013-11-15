# Tests for officedoc module.
import unittest
from plone.app.testing import TEST_USER_ID, setRoles
from plone.namedfile.file import NamedBlobFile
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

    def test_adding(self):
        # we can add OfficeDoc instances
        src = NamedBlobFile(data='Hi there!', filename=u'sample.txt')
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1',
            psj_office_doc = src,
            )
        d1 = self.folder['doc1']
        self.assertTrue(IOfficeDoc.providedBy(d1))
        # additional attributes were set
        self.assertEqual(d1.psj_md5, '396199333edbf40ad43e62a1c1397793')
        assert d1.psj_html_repr.data is not None
        assert d1.psj_pdf_repr.data is not None
