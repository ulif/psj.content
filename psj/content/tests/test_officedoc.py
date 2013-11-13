# Tests for officedoc module.
import unittest
from zope.interface import verify
from psj.content.officedoc import IOfficeDoc, OfficeDoc

class OfficeDocUnitTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill all interface contracts
        obj = OfficeDoc()
        verify.verifyClass(IOfficeDoc, OfficeDoc)
        verify.verifyObject(IOfficeDoc, obj)
