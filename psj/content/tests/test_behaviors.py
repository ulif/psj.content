# tests for psj.content.behaviors
from plone.behavior.interfaces import IBehavior, IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.directives.form import IFormFieldProvider
from zope.component import queryUtility, adapts, provideAdapter
from zope.interface import implements
from zope.schema.interfaces import WrongType
from psj.content.behaviors import (
    IPSJAuthor, IPSJTitle, IPSJSubtitle, IPSJAbstract,
    )
from psj.content.testing import TestCase


class DummyDocument(object):
    # a dummy document that supports properties
    implements(IDexterityContent)
    portal_type = u'testtype'

    def __init__(self, title):
        self.title = title

    def hasProperty(self, key):
        return key in dir(self)

    def setProperty(self, key, val):
        setattr(self, key, val)

    def getProperty(self, key):
        return getattr(self, key)

    def _updateProperty(self, key, val):
        self.setProperty(key, val)


class TestingAssignable(object):
    # a IBehaviorAssignable adapter that adapts DummyContent objects
    implements(IBehaviorAssignable)
    adapts(DummyDocument)

    enabled = [IPSJAuthor, IPSJTitle, IPSJSubtitle, IPSJAbstract]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerate_behaviors(self):
        for e in self.enabled:
            yield queryUtility(IBehavior, name=e.__identifier__)


class MetadataBehaviorsTestCase(TestCase):
    # Tests of behaviors concerning basic PSJ metadata.

    def behavior_installed(self, name, iface):
        # make sure we get the desired behavior after install
        name = u'psj.content.behaviors.%s' % name
        behavior = queryUtility(IBehavior, name=name, default=None)
        self.assertTrue(behavior is not None)
        self.assertEqual(behavior.interface, iface)
        # make sure the behavior provides IFormFieldProvider
        self.assertEqual(
            IFormFieldProvider.providedBy(behavior.interface), True)
        return

    def text_behavior_usable(self, attr_name, iface):
        # we can attach a behavior to a content type and modify some
        # text/textline attribute
        doc = DummyDocument(b'doc')
        provideAdapter(TestingAssignable)
        self.assertEqual(IDexterityContent.providedBy(doc), True)
        behavior = iface(doc, None)
        self.assertTrue(behavior is not None)
        self.assertEqual(True, hasattr(behavior, attr_name))
        # we can assign valid values to doc through the behavior
        setattr(behavior, attr_name, u'John Cleese')
        #behavior.psj_author = u'John Cleese'
        self.assertEqual(u'John Cleese', getattr(doc, attr_name))
        # numbers are not accepted as Text/TextLines
        self.assertRaises(
            WrongType, setattr, behavior, attr_name, 1)
        # also byte streams (non-unicode) are rejected
        self.assertRaises(
            WrongType, setattr, behavior, attr_name, b'Cheese')
        return

    def test_author_installed(self):
        self.behavior_installed('IPSJAuthor', IPSJAuthor)
        return

    def test_author_behavior_usable(self):
        # we can get a behavior by adapter
        self.text_behavior_usable(b'psj_author', IPSJAuthor)
        return

    def test_title_installed(self):
        self.behavior_installed('IPSJTitle', IPSJTitle)
        return

    def test_title_behavior_usable(self):
        # we can get a behavior by adapter
        self.text_behavior_usable(b'psj_title', IPSJTitle)
        return

    def test_subtitle_installed(self):
        self.behavior_installed('IPSJSubtitle', IPSJSubtitle)
        return

    def test_subtitle_behavior_usable(self):
        # we can get a behavior by adapter
        self.text_behavior_usable(b'psj_subtitle', IPSJSubtitle)
        return

    def test_abstract_installed(self):
        self.behavior_installed('IPSJAbstract', IPSJAbstract)
        return

    def test_abstract_behavior_usable(self):
        # we can get a behavior by adapter
        self.text_behavior_usable(b'psj_abstract', IPSJAbstract)
        return
