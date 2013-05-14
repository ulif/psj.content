# tests for psj.content

import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from plone.behavior.interfaces import IBehavior, IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityContent
from plone.directives.form import IFormFieldProvider
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from zope.component import queryUtility, adapts, provideAdapter
from zope.interface import implements
from zope.schema.interfaces import WrongType
ptc.setupPloneSite()

import psj.content
from psj.content.behaviors import IPSJAuthor


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            #zcml.load_config('configure.zcml', psj.content)
            ztc.installPackage(psj.content)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass



class DummyDocument(object):
    # a dummy document that supports properties
    implements(IDexterityContent)
    portal_type = 'testtype'
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

    enabled = [IPSJAuthor]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerate_behaviors(self):
        for e in self.enabled:
            yield queryUtility(IBehavior, name=e.__identifier__)


class BehaviorAuthorTestCase(TestCase):

    def test_author_installed(self):
        # make sure we can get the 'Author' behavior after install
        behavior = queryUtility(
            IBehavior, name='psj.content.behaviors.IPSJAuthor',
            default=None)
        self.assertTrue(behavior is not None)
        self.assertEqual(behavior.interface, IPSJAuthor)
        # make sure the behavior provides IFormFieldProvider
        self.assertEqual(
            IFormFieldProvider.providedBy(behavior.interface), True)
        return

    def test_author_behavior_usable(self):
        # we can get a behavior by adapter
        doc = DummyDocument('doc')
        provideAdapter(TestingAssignable)
        self.assertEqual(IDexterityContent.providedBy(doc), True)
        behavior = IPSJAuthor(doc, None)
        self.assertTrue(behavior is not None)
        self.assertEqual(True, hasattr(behavior, 'psj_author'))
        # we can assign valid values to doc through the behavior
        behavior.psj_author = u'John Cleese'
        self.assertEqual(u'John Cleese', doc.psj_author)
        # numbers are not accepted as TextLines
        self.assertRaises(WrongType, setattr, behavior, 'psj_author', 1)
        # also byte streams (non-unicode) are rejected
        self.assertRaises(WrongType, setattr, behavior, 'psj_author', 'Cheese')
        return


def test_suite():
    suite = unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='psj.content',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='psj.content.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='psj.content',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='psj.content',
        #    test_class=TestCase),

        ])
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BehaviorAuthorTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
