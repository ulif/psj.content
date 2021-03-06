# -*- coding: utf-8 -*-
# Tests for officedoc module.
import unittest
from cStringIO import StringIO
from plone.app.testing import (
    TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, setRoles
    )
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
from zope.component import queryUtility, createObject, getMultiAdapter
from zope.event import notify
from zope.interface import verify
from zope.lifecycleevent import ObjectModifiedEvent
from psj.content.officedoc import IOfficeDoc, OfficeDoc, DisplayView
from psj.content.testing import INTEGRATION_TESTING, FUNCTIONAL_TESTING


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
            psj_office_doc=self.src_file, title=u'My Doc',
            description=u'My description.'
            )
        d1 = self.folder['doc1']
        self.assertTrue(IOfficeDoc.providedBy(d1))
        self.assertEqual(d1.title, u'My Doc')
        self.assertEqual(d1.description, u'My description.')
        # additional attributes were set
        self.assertEqual(d1.psj_md5, '396199333edbf40ad43e62a1c1397793')
        assert d1.psj_html_repr.data is not None
        assert d1.psj_pdf_repr.data is not None

    def test_editing(self):
        # we can modify OfficeDocs. Changes are reflected.
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', psj_office_doc=self.src_file,
            title=u'My doc', description=u'My description.'
            )
        d1 = self.folder['doc1']
        d1.psj_office_doc = NamedBlobFile(
            data='I changed!', filename=u'othersample.txt')
        d1.title = u'My changed title'
        d1.description = u'My changed description'
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        self.assertEqual(d1.psj_md5, '2e2b959667fdf3f17dd3a834b0f1f009')
        self.assertEqual(d1.title, u'My changed title')
        self.assertEqual(d1.description, u'My changed description')

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

    def test_views(self):
        # we can get a regular and a special view for added officedocs
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1',
            psj_office_doc=self.src_file)
        d1 = self.folder['doc1']
        view = d1.restrictedTraverse('@@view')
        assert view is not None
        view = d1.restrictedTraverse('@@psj_view')
        assert isinstance(view, DisplayView)

    def test_default_view(self):
        # `psj_view` is the default.
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', psj_office_doc=self.src_file)
        d1 = self.folder['doc1']
        default_view_name = getMultiAdapter(
            (d1, d1.REQUEST), name="plone_context_state").view_template_id()
        self.assertEqual(default_view_name, 'psj_view')

    def test_searchable_text(self):
        # searchableText contains the office doc content
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', psj_office_doc=self.src_file,
            title=u'Foo Doc', description=u'My Description')
        d1 = self.folder['doc1']
        self.assertEqual(
            'Foo Doc My Description Hi there!',
            d1.SearchableText())

    def test_searchable_text_indexed(self):
        # searchableText is indexed properly
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', psj_office_doc=self.src_file,
            title=u'Foo Doc', description=u'My Description')
        d1 = self.folder['doc1']
        d1.reindexObject()
        result = self.portal.portal_catalog(SearchableText="there")
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].getURL(), d1.absolute_url())

    def test_searchable_text_indexed_after_change(self):
        # when changing an officedoc, also the indexes are updated
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', psj_office_doc=self.src_file)
        d1 = self.folder['doc1']
        d1.psj_office_doc = NamedBlobFile(
            data='I changed!', filename=u'othersample.txt')
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        result = self.portal.portal_catalog(SearchableText="there")
        self.assertEqual(0, len(result))  # old content not indexed
        result = self.portal.portal_catalog(SearchableText="changed")
        self.assertEqual(1, len(result))  # new content found
        self.assertEqual(result[0].getURL(), d1.absolute_url())

    def test_title_indexed(self):
        # titles of officedocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1', title=u'My DocTitle')
        d1 = self.folder['doc1']
        result = self.portal.portal_catalog(Title='DocTitle')
        self.assertEqual(1, len(result))
        # title changes are reflected in catalog
        d1.setTitle(u'My Othertitle')
        notify(ObjectModifiedEvent(d1))
        result = self.portal.portal_catalog(Title='Doctitle')
        self.assertEqual(0, len(result))  # old content gone
        result = self.portal.portal_catalog(Title='Othertitle')
        self.assertEqual(1, len(result))  # new content found

    def test_description_indexed(self):
        # descriptions of officedocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.officedoc', 'doc1',
            description=u'My DocDescription')
        d1 = self.folder['doc1']
        result = self.portal.portal_catalog(Description='DocDescription')
        self.assertEqual(1, len(result))
        # description changes are reflected in catalog
        d1.setDescription(u'My ChangedDescription')
        notify(ObjectModifiedEvent(d1))
        result = self.portal.portal_catalog(Description='DocDescription')
        self.assertEqual(0, len(result))  # old content gone
        result = self.portal.portal_catalog(Description='ChangedDescription')
        self.assertEqual(1, len(result))  # new content found


class OfficeDocBrowserTests(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.src_file = NamedBlobFile(
            data='Hi there!', filename=u'sample.txt')

    def do_login(self, browser):
        browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,))

    def create_doc(self):
        portal = self.layer['portal']
        portal.invokeFactory(
            'psj.content.officedoc', 'myeditdoc',
            psj_office_doc=self.src_file, title=u'My Edit Doc',
            description=u'My description.'
            )
        import transaction
        transaction.commit()

    def test_add(self):
        # we can add office docs
        self.do_login(self.browser)
        self.browser.open(self.portal_url)
        # find add link and click it
        add_link = self.browser.getLink('Office Document')
        self.assertEqual('psj-content-officedoc', add_link.attrs['id'])
        add_link.click()

        # fill form
        self.browser.getControl(label='Title').value = 'My Title'
        self.browser.getControl(label='Summary').value = 'My Description'
        # upload source document
        file_upload = self.browser.getControl(
            name='form.widgets.psj_office_doc')
        myfile = StringIO('My File Contents')
        file_upload.add_file(myfile, 'text/plain', 'sample.txt')
        self.browser.getControl("Save").click()

        assert 'My Title' in self.browser.contents
        assert 'My Description' in self.browser.contents
        assert 'My File Contents' in self.browser.contents
        assert 'sample.txt.pdf' in self.browser.contents

    def test_edit(self):
        # we can edit office docs
        self.do_login(self.browser)
        self.create_doc()
        self.browser.open(self.portal_url + '/myeditdoc')
        edit_link = self.browser.getLink('Edit', index=1)
        edit_link.click()

        # set new values
        self.browser.getControl(label='Title').value = 'Other Title'
        self.browser.getControl(label='Summary').value = 'My Other Descr.'
        # upload new source
        file_upload = self.browser.getControl(
            name='form.widgets.psj_office_doc')
        myfile = StringIO('My Other File')
        file_upload.add_file(myfile, 'text/plain', 'other.txt')
        # also 'check' the 'Replace file' radio checkbox
        replace_ctl = self.browser.getControl(
            name="form.widgets.psj_office_doc.action")
        replace_ctl.value = ['replace']
        self.browser.getControl("Save").click()

        assert 'Other Title' in self.browser.contents
        assert 'My Other Title' not in self.browser.contents
        assert 'My Other Descr.' in self.browser.contents
        assert 'My Description' not in self.browser.contents
        assert 'My Other File' in self.browser.contents
        assert 'My File Contents' not in self.browser.contents
        assert 'other.txt.pdf' in self.browser.contents
        assert 'sample.txt.pdf' not in self.browser.contents
