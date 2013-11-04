# tests for psj.content

import unittest
#from zope.testing import doctestunit
#from zope.component import testing


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
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest=u'test_suite')
