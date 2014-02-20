# -*- coding: utf-8 -*-
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
"""ZCML directives.

"""
from zope.component.zcml import handler
from psj.content.interfaces import IExternalVocabConfig


def external_vocab_conf(context, path, name):
    """Handler for ZCML ``external-vocab`` directive.

    Register a named global utility under IExternalVocabConfig, named
    as `name` and containing a directory with some entries that
    identify the vocab to register more thoroughly.  ``path``.

    Interested parties can ask for external vocabs like this:

      >>> from psj.content.interfaces import IExternalVocabConfig
      >>> from zope.component import queryUtility
      >>> conf = queryUtility(IExternalVocabConfig, name='foo.bar')

    Then, if `conf` is not ``None``, you can get the configured
    parameters set in ``site.zcml`` (or other ZCML files parsed during
    startup).

      >>> conf['path']
      /foo/bar

      >>> conf['name']
      'foo.bar'

    """
    context.action(
        discriminator=('utility', IExternalVocabConfig, name),
        callable=handler,
        args=('registerUtility',
              {'path': path, 'name': name},
              IExternalVocabConfig,
              name)
        )
