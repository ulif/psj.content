# -*- coding: utf-8 -*-
#
#  psj.content is copyright (c) 2014 Uli Fouquet
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
import os
import shutil
import tempfile
from plone.app.testing import (
    PloneSandboxLayer, PLONE_FIXTURE, IntegrationTesting,
    FunctionalTesting, pushGlobalRegistry, popGlobalRegistry, ploneSite
    )
from zope.component import getGlobalSiteManager
from psj.content.interfaces import IExternalVocabConfig


class ExternalVocabSetup(object):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def create_external_vocab(self, name, valid_path=True):
        # create a working external vocab and register it
        gsm = getGlobalSiteManager()
        path = os.path.join(self.workdir, 'sample_vocab.csv')
        if valid_path:
            open(path, 'w').write(
                u'Vocab Entry 1\nVocab Entry 2\nÜmlaut Entry\n'.encode(
                    'utf-8'))
        conf = {'path': path, 'name': name}
        gsm.registerUtility(conf, provided=IExternalVocabConfig, name=name)


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUp(self):
        with ploneSite() as portal:
            pushGlobalRegistry(portal)
        super(Fixture, self).setUp()

    def tearDown(self):
        super(Fixture, self).tearDown()
        with ploneSite() as portal:
            popGlobalRegistry(portal)

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
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='psj.content:Functional',
    )
