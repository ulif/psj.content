# -*- coding: utf-8 -*-
# Tests for psj_baseretrodoc module.
#
import os
import shutil
import tempfile
import unittest
from base64 import b64encode
from plone.app.testing import (
    TEST_USER_ID, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, setRoles,
    )
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from zope.component import queryUtility, createObject, getGlobalSiteManager
from zope.event import notify
from zope.interface import verify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory
from psj.content.interfaces import IExternalVocabConfig
from psj.content.psj_baseretrodoc import (
    IBaseRetroDoc, BaseRetroDoc,
    )
from psj.content.testing import INTEGRATION_TESTING, FUNCTIONAL_TESTING


VOCABS = [
    (u'psj.content.Institutes', 'Institute'),
    (u'psj.content.Licenses', 'License')
    ]

RICH_TEXT_VALUE1 = RichTextValue(
    u"My Richtext Value\n",
    'text/plain', 'text/x-html-safe', 'utf-8')

RICH_TEXT_VALUE2 = RichTextValue(
    u"Other Richtext Value\n",
    'text/plain', 'text/x-html-safe', 'utf-8')


class BaseRetroDocUnitTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill all interface contracts
        obj = BaseRetroDoc()
        verify.verifyClass(IBaseRetroDoc, BaseRetroDoc)
        verify.verifyObject(IBaseRetroDoc, obj)


class BaseRetroDocIntegrationTests(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def create_external_vocab(self, name, readable=None):
        # create a working external vocab and register it
        readable = readable or name
        gsm = getGlobalSiteManager()
        path = os.path.join(self.workdir, 'sample_vocab-%s.csv' % name)
        entries = u'First %s Entry\nOther %s Entry\nÜmlautEntry\n' % (
            readable, readable)
        open(path, 'w').write(entries.encode('utf-8'))
        conf = {'path': path, 'name': name}
        gsm.registerUtility(conf, provided=IExternalVocabConfig, name=name)

    def setup_vocabs(self):
        for name, readable in VOCABS:
            self.create_external_vocab(name, readable)

    def teardown_vocabs(self):
        gsm = getGlobalSiteManager()
        for entry in VOCABS:
            gsm.unregisterUtility(name=entry[0], provided=IVocabularyFactory)

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']
        self.setup_vocabs()
        return

    def tearDown(self):
        self.teardown_vocabs()
        shutil.rmtree(self.workdir)

    def test_adding(self):
        # we can add BaseRetroDoc instances
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',
            title=u'My Doc', description=u'My description.',
            psj_author=[u'I', u'Me', u'Myself'],
            psj_title=u'My Title', psj_subtitle=u'My Subtitle',
            psj_pages=u'1-99', psj_institute=[u'First Institute Entry'],
            psj_license=u'First License Entry',
            psj_abstract=RICH_TEXT_VALUE1,
            psj_doi=u'My Identifier',
            )
        d1 = self.folder['doc1']
        self.assertTrue(IBaseRetroDoc.providedBy(d1))
        self.assertEqual(d1.title, u'My Doc')
        self.assertEqual(d1.description, u'My description.')
        # additional attributes were set
        self.assertEqual(d1.psj_author, [u'I', u'Me', u'Myself'])
        self.assertEqual(d1.psj_title, u'My Title')
        self.assertEqual(d1.psj_subtitle, u'My Subtitle')
        self.assertEqual(d1.psj_pages, u'1-99')
        self.assertEqual(d1.psj_institute, [u'First Institute Entry', ])
        self.assertEqual(d1.psj_license, u'First License Entry')
        self.assertEqual(d1.psj_abstract.output,
                         u'<p>My Richtext Value</p>')
        self.assertEqual(d1.psj_doi, u'My Identifier')

    def test_editing(self):
        # we can modify BaseRetroDocs. Changes are reflected.
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',
            title=u'My doc', description=u'My description.',
            psj_author=[u'My Author'],
            psj_title=u'My title', psj_subtitle=u'My Subtitle',
            psj_pages=u'1-99',
            psj_institute=[u'First Institute Entry', ],
            psj_license=u'First License Entry',
            psj_abstract=RICH_TEXT_VALUE1,
            psj_doi=u'My Identifier',
            )
        d1 = self.folder['doc1']
        d1.title = u'My changed title'
        d1.description = u'My changed description'
        d1.psj_author = [u'My changed author', ]
        d1.psj_title = u'My changed title'
        d1.psj_subtitle = u'My changed subtitle'
        d1.psj_pages = u'100-199'
        d1.psj_institute = [u'Other Institute Entry', ]
        d1.psj_license = u'Other License Entry'
        d1.psj_abstract = RICH_TEXT_VALUE2
        d1.psj_doi = u'My changed identifier'
        # we have to fire an event here
        notify(ObjectModifiedEvent(d1))
        self.assertEqual(d1.title, u'My changed title')
        self.assertEqual(d1.description, u'My changed description')
        self.assertEqual(d1.psj_author, [u'My changed author', ])
        self.assertEqual(d1.psj_title, u'My changed title')
        self.assertEqual(d1.psj_subtitle, u'My changed subtitle')
        self.assertEqual(d1.psj_pages, u'100-199')
        self.assertEqual(d1.psj_institute, [u'Other Institute Entry', ])
        self.assertEqual(d1.psj_license, u'Other License Entry')
        self.assertEqual(d1.psj_abstract.output,
                         u'<p>Other Richtext Value</p>')
        self.assertEqual(d1.psj_doi, u'My changed identifier')

    def test_fti(self):
        # we can get factory type infos for base docs
        fti = queryUtility(IDexterityFTI, name='psj.content.baseretrodoc')
        assert fti is not None

    def test_schema(self):
        # our fti provides the correct schema
        fti = queryUtility(IDexterityFTI, name='psj.content.baseretrodoc')
        schema = fti.lookupSchema()
        self.assertEqual(IBaseRetroDoc, schema)

    def test_factory(self):
        # our fti provides a factory for BaseRetroDoc instances
        fti = queryUtility(IDexterityFTI, name='psj.content.baseretrodoc')
        factory = fti.factory
        new_obj = createObject(factory)
        self.assertTrue(IBaseRetroDoc.providedBy(new_obj))

    def test_views(self):
        # we can get a regular and a special view for added baseretrodocs
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',)
        d1 = self.folder['doc1']
        view = d1.restrictedTraverse('@@view')
        assert view is not None

    def test_searchable_text(self):
        # searchableText contains the base doc content
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor', psj_doi=u'Bar',
            psj_abstract=RICH_TEXT_VALUE1,
            )
        d1 = self.folder['doc1']
        self.assertEqual(
            'Foo Doc My Description Baz Furor My Richtext Value',
            d1.SearchableText())

    def test_searchable_text_indexed(self):
        # searchableText is indexed properly
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',
            title=u'Foo Doc', description=u'My Description',
            psj_title=u'Baz', psj_subtitle=u'Furor', psj_doi=u'Bar',
            )
        d1 = self.folder['doc1']
        d1.reindexObject()
        result = self.portal.portal_catalog(SearchableText="Foo")
        self.assertEqual(1, len(result))
        self.assertEqual(result[0].getURL(), d1.absolute_url())

    def test_title_indexed(self):
        # titles of baseretrodocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1', title=u'My DocTitle',
            psj_doi=u'Bar',)
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
        # descriptions of baseretrodocs are indexed (also after change)
        self.folder.invokeFactory(
            'psj.content.baseretrodoc', 'doc1',
            description=u'My DocDescription', psj_doi=u'Bar')
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

    layer = FUNCTIONAL_TESTING

    def create_doc(self):
        portal = self.layer['portal']
        portal.invokeFactory(
            'psj.content.baseretrodoc', 'myeditdoc',
            title=u'My Edit Doc', description=u'My description.',
            psj_author=[u'My Author', ],
            psj_title=u'My Title', psj_subtitle=u'My Subtitle',
            psj_pages=u'1-99',
            psj_institute=[u'First Institute Entry', ],
            psj_license=u'First License Entry',
            psj_abstract=RICH_TEXT_VALUE1,
            psj_doi=u'My identifier',
            )
        import transaction
        transaction.commit()

    def create_external_vocab(self, name, readable=None):
        # create a working external vocab and register it
        readable = readable or name
        gsm = getGlobalSiteManager()
        path = os.path.join(self.workdir, 'sample_vocab-%s.csv' % name)
        entries = u'First %s Entry\nOther %s Entry\nÜmlautEntry\n' % (
            readable, readable)
        open(path, 'w').write(entries.encode('utf-8'))
        conf = {'path': path, 'name': name}
        gsm.registerUtility(conf, provided=IExternalVocabConfig, name=name)

    def setup_vocabs(self):
        for name, readable in VOCABS:
            self.create_external_vocab(name, readable)

    def teardown_vocabs(self):
        gsm = getGlobalSiteManager()
        for name in VOCABS:
            gsm.unregisterUtility(name=name[0], provided=IVocabularyFactory)

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.layer['app'])
        self.workdir = tempfile.mkdtemp()
        self.setup_vocabs()

    def tearDown(self):
        self.teardown_vocabs()
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
        add_link = self.browser.getLink('PSJ Base Retro Document')
        self.assertEqual('psj-content-baseretrodoc', add_link.attrs['id'])
        add_link.click()

        # fill form
        self.browser.getControl(label='Autor').value = 'My Author'
        self.browser.getControl(label='Title').value = 'My Title'
        self.browser.getControl(label='Summary').value = 'My Description'
        self.browser.getControl(label='Titel').value = 'My Book Title'
        self.browser.getControl(label='Untertitel').value = 'My Subtitle'
        self.browser.getControl(label='Seiten').value = '1-99'
        # XXX: Disabled; too hard to test JS-driven forms
        #self.browser.getControl(label='Institut').displayValue = [
        #    'First Institute Entry', ]
        self.browser.getControl(label='Lizenz').displayValue = [
            'First License Entry', ]
        self.browser.getControl(
            name='form.widgets.psj_abstract').value = 'My Abstract\n'
        self.browser.getControl(label='DOI').value = 'My Identifier'
        self.browser.getControl("Save").click()

        assert 'My Title' in self.browser.contents
        assert 'My Description' in self.browser.contents
        assert 'My Author' in self.browser.contents
        assert 'My Book Title' in self.browser.contents
        assert 'My Subtitle' in self.browser.contents
        assert '1-99' in self.browser.contents
        # XXX: Disabled; too hard to test JS-driven forms
        #assert 'First Institute Entry' in self.browser.contents
        assert 'First License Entry' in self.browser.contents
        assert 'My Abstract' in self.browser.contents
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
        self.browser.getControl(label='Autor').value = 'Other Author'
        self.browser.getControl(label='Titel').value = 'Other Book Title'
        self.browser.getControl(label='Untertitel').value = 'Other Subtitle'
        self.browser.getControl(label='Seiten').value = '100-999'
        # XXX: Disabled; too hard to test JS-driven forms
        #self.browser.getControl(label='Institut').value = [
        #    b64encode('Other Institute Entry'), ]
        self.browser.getControl(label='Lizenz').value = [
            b64encode('Other License Entry'), ]
        self.browser.getControl(
            name='form.widgets.psj_abstract').value = 'Other Abstract\n'
        self.browser.getControl(label='DOI').value = 'Other Identifier'
        self.browser.getControl("Save").click()

        assert 'Other Title' in self.browser.contents
        assert 'My Title' not in self.browser.contents
        assert 'My Other Descr.' in self.browser.contents
        assert 'My Description' not in self.browser.contents
        assert 'Other Author' in self.browser.contents
        assert 'My Author' not in self.browser.contents
        assert 'Other Book Title' in self.browser.contents
        assert 'My Book Title' not in self.browser.contents
        assert 'Other Subtitle' in self.browser.contents
        assert 'My Subtitle' not in self.browser.contents
        assert '100-999' in self.browser.contents
        assert '1-99' not in self.browser.contents
        # XXX: Disabled; too hard to test JS-driven forms
        #assert 'Other Institute Entry' in self.browser.contents
        #assert 'First Institute Entry' not in self.browser.contents
        assert 'Other License Entry' in self.browser.contents
        assert 'First License Entry' not in self.browser.contents
        assert 'Other Abstract' in self.browser.contents
        assert 'My Abstract' not in self.browser.contents
        assert 'Other Identifier' in self.browser.contents
        assert 'My Identifier' not in self.browser.contents
