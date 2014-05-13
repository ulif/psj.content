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
from plone.testing import Layer
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

    def create_external_vocab_from_choice(
        self, iface, attr_name, is_list=False):
        """Create an external vocab from a choice field.
        """
        choice = iface[attr_name]
        if is_list:
            choice = choice.value_type
        binder = choice.vocabulary
        v_name = binder.name
        self.create_external_vocab(v_name)
        return v_name, binder

    def create_external_vocab_from_choicelist(self, iface, attr_name):
        """Create an external vocab from a list of choices field.
        """
        return self.create_external_vocab_from_choice(
            iface, attr_name, is_list=True)


class RedisStoreSetup(Layer):
    """A test layer class for a layer that starts a redis server.

    The server is torn down after tests within layer. An active
    instance of this layer is available as `RedisLayer`.

    You should call `flushdb` for any client created during tests.

    From within tests the running server instance can be accessed via
    `layer['redis_server']`.
    """
    def setUp(self):
        # A complicate way to mimic 'from testing.redis import RedisServer'
        # This is needed because the external package name (`testing`)
        # is shadowed by the local module named `testing`. `testing.redis`
        # can therefore not be found, normally.
        redis_mod = __import__('testing.redis', (), (), ['RedisServer', ], 0)
        RedisServer = redis_mod.RedisServer
        self['redis_server'] = RedisServer()
        super(RedisStoreSetup, self).setUp()

    def tearDown(self):
        super(RedisStoreSetup, self).tearDown()
        self['redis_server'].stop()


#: A test layer that provides a Redis Server.
#:
#: Please see `RedisStoreSetup` for details. `RedisLayer` is an instance
#: of `RedisStoreSetup` class.
RedisLayer = RedisStoreSetup()


class Fixture(PloneSandboxLayer):

    defaultBases = (RedisLayer, PLONE_FIXTURE,)

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
REDIS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE, RedisLayer,),
    name='psj.content:Integration-redis',
    )
