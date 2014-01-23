#  psj.content is copyright (c) 2013 Uli Fouquet
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#  MA 02111-1307 USA.
#
"""Testing support for `psj.content`.

"""
from plone.app.testing import (
    PloneSandboxLayer, PLONE_FIXTURE, IntegrationTesting,
    FunctionalTesting
    )
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc

ptc.setupPloneSite()


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            import psj.content
            fiveconfigure.debug_mode = True
            ztc.installPackage(psj.content)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configuration_context):
        # load ZCML
        import psj.content
        self.loadZCML(package=psj.content)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'psj.content:default')
        self.applyProfile(portal, 'psj.policy:default')

FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='psj.content:Integration',
    )
FUCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='psj.content:Functional',
    )
