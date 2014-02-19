# -*- coding: utf-8 -*-
# Tests for psj_basedoc module.
import unittest
from plone.app.testing import (
    TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, setRoles,
    )
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from zope.component import queryUtility, createObject, getGlobalSiteManager
from zope.event import notify
from zope.interface import verify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory
from psj.content.psj_basedoc import (
    IBaseDoc, BaseDoc,
    )
from psj.content.testing import INTEGRATION_TESTING, SampleVocabFactory


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
        vocab_factory = SampleVocabFactory()
        self.portal.getSiteManager().registerUtility(
            vocab_factory, provided=IVocabularyFactory,
            name=u'psj.content.Institutes')

    def test_adding(self):
        # we can add BaseDoc instances
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'My Doc', description=u'My description.',
            psj_title=u'My Title', psj_subtitle=u'My Subtitle',
            psj_institute='InstOne',
            )
        d1 = self.folder['doc1']
        self.assertTrue(IBaseDoc.providedBy(d1))
        self.assertEqual(d1.title, u'My Doc')
        self.assertEqual(d1.description, u'My description.')
        # additional attributes were set
        self.assertEqual(d1.psj_title, u'My Title')
        self.assertEqual(d1.psj_subtitle, u'My Subtitle')
        self.assertEqual(d1.psj_institute, 'InstOne')

    def test_editing(self):
        # we can modify BaseDocs. Changes are reflected.
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'My doc', description=u'My description.',
            psj_title=u'My title', psj_subtitle=u'My Subtitle',
            psj_institute=u'InstOne',
            )
        d1 = self.folder['doc1']
        d1.title = u'My changed title'
        d1.description = u'My changed description'
        d1.psj_title = u'My changed title'
        d1.psj_subtitle = u'My changed subtitle'
        d1.psj_institute = u'InstTwo'
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        self.assertEqual(d1.title, u'My changed title')
        self.assertEqual(d1.description, u'My changed description')
        self.assertEqual(d1.psj_title, u'My changed title')
        self.assertEqual(d1.psj_subtitle, u'My changed subtitle')
        self.assertEqual(d1.psj_institute, u'InstTwo')

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
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor',
            )
        d1 = self.folder['doc1']
        self.assertEqual(
            'Foo Doc My Description',
            d1.SearchableText())

    def test_searchable_text_indexed(self):
        # searchableText is indexed properly
        self.folder.invokeFactory(
            'psj.content.basedoc', 'doc1',
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor',
            )
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

    def setup_vocabs(self):
        vocab_factory = SampleVocabFactory()
        gsm = getGlobalSiteManager()
        gsm.registerUtility(
            vocab_factory, provided=IVocabularyFactory,
            name=u'psj.content.Institutes')

    def teardown_vocabs(self):
        gsm = getGlobalSiteManager()
        for name in [u'psj.content.Institutes', ]:
            gsm.unregisterUtility(name=name, provided=IVocabularyFactory)

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.setup_vocabs()

    def tearDown(self):
        self.teardown_vocabs()

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
        self.browser.getControl(label='Titel').value = 'My Book Title'
        self.browser.getControl(label='Untertitel').value = 'My Subtitle'
        self.browser.getControl(label='Institut').value = ['InstOne', ]
        self.browser.getControl("Save").click()

        assert 'My Title' in self.browser.contents
        assert 'My Description' in self.browser.contents
        assert 'My Book Title' in self.browser.contents
        assert 'My Subtitle' in self.browser.contents
        assert 'InstOne' in self.browser.contents

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
        self.browser.getControl(label='Titel').value = 'Other Book Title'
        self.browser.getControl(label='Untertitel').value = 'Other Subtitle'
        self.browser.getControl(label='Institut').value = ['InstTwo', ]
        self.browser.getControl("Save").click()

        assert 'Other Title' in self.browser.contents
        assert 'My Other Title' not in self.browser.contents
        assert 'My Other Descr.' in self.browser.contents
        assert 'My Description' not in self.browser.contents
        assert 'Other Book Title' in self.browser.contents
        assert 'My Book Title' not in self.browser.contents
        assert 'Other Subtitle' in self.browser.contents
        assert 'My Subtitle' not in self.browser.contents
        assert 'InstTwo' in self.browser.contents
        assert 'InstOne' not in self.browser.contents
