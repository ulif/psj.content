# tests for psj.content

import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from plone.behavior.interfaces import IBehavior
from plone.directives.form import IFormFieldProvider
from Products.CMFDefault.Document import Document
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from zope.component import queryUtility
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
