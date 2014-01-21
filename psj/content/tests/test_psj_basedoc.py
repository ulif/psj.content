# -*- coding: utf-8 -*-
# Tests for psj_basedoc module.
import unittest
from cStringIO import StringIO
from plone.app.testing import (
    TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD,
    SITE_OWNER_NAME, SITE_OWNER_PASSWORD,
    setRoles, login, logout,
    )
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
from zope.component import queryUtility, createObject, getMultiAdapter
from zope.event import notify
from zope.interface import verify
from zope.lifecycleevent import ObjectModifiedEvent
from psj.content.psj_basedoc import (
    IBaseDoc, BaseDoc,
    )
from psj.content.testing import INTEGRATION_TESTING


class BaseDocUnitTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill all interface contracts
        obj = BaseDoc()
        verify.verifyClass(IBaseDoc, BaseDoc)
        verify.verifyObject(IBaseDoc, obj)


class BaseDocIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

    def test_adding(self):
        # we can add BaseDoc instances
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'My Doc', description=u'My description.'
            )
        d1 = self.folder['doc1']
        self.assertTrue(IBaseDoc.providedBy(d1))
        self.assertEqual(d1.title, u'My Doc')
        self.assertEqual(d1.description, u'My description.')
        # additional attributes were set

    def test_editing(self):
        # we can modify BaseDocs. Changes are reflected.
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'My doc', description=u'My description.'
            )
        d1 = self.folder['doc1']
        d1.title = u'My changed title'
        d1.description = u'My changed description'
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        self.assertEqual(d1.title, u'My changed title')
        self.assertEqual(d1.description, u'My changed description')

    def test_fti(self):
        # we can get factory type infos for base docs
        fti = queryUtility(IDexterityFTI, name='psj.content.basedoc')
        assert fti is not None

    def test_schema(self):
        # our fti provides the correct schema
        fti = queryUtility(IDexterityFTI, name='psj.content.basedoc')
        schema = fti.lookupSchema()
        self.assertEqual(IBaseDoc, schema)

    def test_factory(self):
        # our fti provides a factory for BaseDoc instances
        fti = queryUtility(IDexterityFTI, name='psj.content.basedoc')
        factory = fti.factory
        new_obj = createObject(factory)
        self.assertTrue(IBaseDoc.providedBy(new_obj))

    def test_views(self):
        # we can get a regular and a special view for added basedocs
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',)
        d1 = self.folder['doc1']
        view = d1.restrictedTraverse('@@view')
        assert view is not None

    def test_searchable_text(self):
        # searchableText contains the base doc content
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'Foo Doc', description=u'My Description')
        d1 = self.folder['doc1']
        self.assertEqual(
            'Foo Doc My Description',
            d1.SearchableText())

    def test_searchable_text_indexed(self):
        # searchableText is indexed properly
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'Foo Doc', description=u'My Description')
        d1 = self.folder['doc1']
        d1.reindexObject()
        result = self.portal.portal_catalog(SearchableText="Foo")
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].getURL(), d1.absolute_url())

    def test_title_indexed(self):
        # titles of basedocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1', title=u'My DocTitle')
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
        # descriptions of basedocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
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


class BasedocBrowserTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])

    def do_login(self, browser):
        browser.open(self.portal_url + '/login')
        browser.getControl(label='Login Name').value = SITE_OWNER_NAME
        browser.getControl(label='Password').value = SITE_OWNER_PASSWORD
        browser.getControl("Log in").click()

    def test_add(self):
        # we can add base docs (and edit it; see below)
        self.do_login(self.browser)
        self.browser.open(self.portal_url)
        # find add link and click it
        add_link = self.browser.getLink('PSJ Base Document')
        self.assertEqual('psj-content-basedoc', add_link.attrs['id'])
        add_link.click()

        # fill form
        self.browser.getControl(label='Title').value = 'My Title'
        self.browser.getControl(label='Summary').value = 'My Description'
        self.browser.getControl("Save").click()

        assert 'My Title' in self.browser.contents
        assert 'My Description' in self.browser.contents

        # edit tests follow here.

        # XXX: These should be in a separate test, but it looks as
        # test isolation does not work sufficiently: the my-title doc
        # created above shows up in other tests in this browser test
        # case. Therefore we do the edit tests right here.
        edit_link = self.browser.getLink('Edit')
        edit_link.click()

        # set new values
        self.browser.getControl(label='Title').value = 'Other Title'
        self.browser.getControl(label='Summary').value = 'My Other Descr.'
        self.browser.getControl("Save").click()

        assert 'Other Title' in self.browser.contents
        assert 'My Other Title' not in self.browser.contents
        assert 'My Other Descr.' in self.browser.contents
        assert 'My Description' not in self.browser.contents