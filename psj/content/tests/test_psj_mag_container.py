# -*- coding: utf-8 -*-
# Tests for psj_mag_container module.
#
# XXX: FSD-related tests (including author attr) are missing.
#      These are blocked by difficulties installing FSD in tests.
#
import shutil
import tempfile
import unittest
from plone.app.testing import (
    TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, setRoles,
    )
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from zope.component import queryUtility, createObject
from zope.event import notify
from zope.interface import verify
from zope.lifecycleevent import ObjectModifiedEvent
from psj.content.psj_mag_container import (
    IPSJMagazineContainer, PSJMagazineContainer,
    )
from psj.content.testing import INTEGRATION_TESTING, FUNCTIONAL_TESTING


class PSJMagazineContainerUnitTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill all interface contracts
        obj = PSJMagazineContainer()
        verify.verifyClass(IPSJMagazineContainer, PSJMagazineContainer)
        verify.verifyObject(IPSJMagazineContainer, obj)


class PSJMagazineContainerIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        return

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_adding(self):
        # we can add PSJMagazineContainer instances
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',
            title=u'My Doc', description=u'My description.',
            psj_title=u'My Title', psj_subtitle=u'My Subtitle',
            psj_publication_year=u"2014",
            psj_urn=u'My Identifier',
            )
        d1 = self.folder['doc1']
        self.assertTrue(IPSJMagazineContainer.providedBy(d1))
        self.assertEqual(d1.title, u'My Doc')
        self.assertEqual(d1.description, u'My description.')
        # additional attributes were set
        self.assertEqual(d1.psj_title, u'My Title')
        self.assertEqual(d1.psj_subtitle, u'My Subtitle')
        self.assertEqual(d1.psj_publication_year, u'2014')
        self.assertEqual(d1.psj_urn, u'My Identifier')

    def test_editing(self):
        # we can modify PSJMagazineContainers. Changes are reflected.
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',
            title=u'My doc', description=u'My description.',
            psj_title=u'My title', psj_subtitle=u'My Subtitle',
            psj_doi=u'My Identifier',
            )
        d1 = self.folder['doc1']
        d1.title = u'My changed title'
        d1.description = u'My changed description'
        d1.psj_title = u'My changed title'
        d1.psj_subtitle = u'My changed subtitle'
        d1.psj_publication_year = u'1969'
        d1.psj_urn = u'My changed identifier'
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        self.assertEqual(d1.title, u'My changed title')
        self.assertEqual(d1.description, u'My changed description')
        self.assertEqual(d1.psj_title, u'My changed title')
        self.assertEqual(d1.psj_subtitle, u'My changed subtitle')
        self.assertEqual(d1.psj_publication_year, u'1969')
        self.assertEqual(d1.psj_urn, u'My changed identifier')

    def test_fti(self):
        # we can get factory type infos for base docs
        fti = queryUtility(IDexterityFTI, name='psj.content.magcontainer')
        assert fti is not None

    def test_schema(self):
        # our fti provides the correct schema
        fti = queryUtility(IDexterityFTI, name='psj.content.magcontainer')
        schema = fti.lookupSchema()
        self.assertEqual(IPSJMagazineContainer, schema)

    def test_factory(self):
        # our fti provides a factory for PSJMagazineContainer instances
        fti = queryUtility(IDexterityFTI, name='psj.content.magcontainer')
        factory = fti.factory
        new_obj = createObject(factory)
        self.assertTrue(IPSJMagazineContainer.providedBy(new_obj))

    def test_views(self):
        # we can get a regular and a special view for added magcontainers
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',)
        d1 = self.folder['doc1']
        view = d1.restrictedTraverse('@@view')
        assert view is not None

    def test_searchable_text(self):
        # searchableText contains the mag container content values
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor', psj_urn=u'Bar',
            psj_publication_year=u'2014',
            )
        d1 = self.folder['doc1']
        self.assertEqual(
            'Foo Doc My Description Baz Furor 2014 Bar',
            d1.SearchableText())

    def test_searchable_text_indexed(self):
        # searchableText is indexed properly
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor', psj_urn=u'Bar',
            psj_publication_year=u'2014',
            )
        d1 = self.folder['doc1']
        d1.reindexObject()
        result = self.portal.portal_catalog(SearchableText="Foo")
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].getURL(), d1.absolute_url())

    def test_title_indexed(self):
        # titles of magcontainers are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1', title=u'My DocTitle',
            psj_urn=u'Bar',)
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
        # descriptions of magcontainers are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.magcontainer', 'doc1',
            description=u'My DocDescription', psj_urn=u'Bar')
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


class PSJMagazineContainerBrowserTests(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def create_doc(self):
        portal = self.layer['portal']
        portal.invokeFactory(
            'psj.content.magcontainer', 'myeditdoc',
            title=u'My Edit Doc', description=u'My description.',
            psj_title=u'My Title', psj_subtitle=u'My Subtitle',
            psj_publication_year=u'Year No 1', psj_urn=u'My identifier',
            )
        import transaction
        transaction.commit()

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def do_login(self, browser):
        browser.open(self.portal_url + '/login')
        browser.getControl(label='Login Name').value = SITE_OWNER_NAME
        browser.getControl(label='Password').value = SITE_OWNER_PASSWORD
        browser.getControl("Log in").click()

    def test_add(self):
        # we can add base docs.
        self.do_login(self.browser)
        self.browser.open(self.portal_url)
        # find add link and click it
        add_link = self.browser.getLink('PSJ Magazine Container')
        self.assertEqual('psj-content-magcontainer', add_link.attrs['id'])
        add_link.click()

        # fill form
        self.browser.getControl(label='Title').value = 'My Title'
        self.browser.getControl(label='Summary').value = 'My Description'
        self.browser.getControl(label='Titel').value = 'My Book Title'
        self.browser.getControl(label='Untertitel').value = 'My Subtitle'
        self.browser.getControl(
            label='Ersterscheinungsdatum').value = 'My Date'
        self.browser.getControl(label='URN').value = 'My Identifier'
        self.browser.getControl("Save").click()

        assert 'My Title' in self.browser.contents
        assert 'My Description' in self.browser.contents
        assert 'My Book Title' in self.browser.contents
        assert 'My Subtitle' in self.browser.contents
        assert 'My Date' in self.browser.contents
        assert 'My Identifier' in self.browser.contents

    def test_edit(self):
        # we can edit base docs
        self.do_login(self.browser)
        self.create_doc()
        self.browser.open(self.portal_url + '/myeditdoc')
        edit_link = self.browser.getLink('Edit', index=1)
        edit_link.click()

        # set new values
        self.browser.getControl(label='Title').value = 'Other Title'
        self.browser.getControl(label='Summary').value = 'My Other Descr.'
        self.browser.getControl(label='Titel').value = 'Other Book Title'
        self.browser.getControl(label='Untertitel').value = 'Other Subtitle'
        self.browser.getControl(
            label='Ersterscheinungsdatum').value = 'Year No 2'
        self.browser.getControl(label='URN').value = 'Other Identifier'
        self.browser.getControl("Save").click()

        assert 'Other Title' in self.browser.contents
        assert 'My Title' not in self.browser.contents
        assert 'My Other Descr.' in self.browser.contents
        assert 'My Description' not in self.browser.contents
        assert 'Other Book Title' in self.browser.contents
        assert 'My Book Title' not in self.browser.contents
        assert 'Other Subtitle' in self.browser.contents
        assert 'My Subtitle' not in self.browser.contents
        assert 'Year No 2' in self.browser.contents
        assert 'Year No 1' not in self.browser.contents
        assert 'Other Identifier' in self.browser.contents
        assert 'My Identifier' not in self.browser.contents
