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
"""Sources (in the zope.schema sense) and source context binders.

"""
import os
from base64 import b64encode
from five import grok
from zope.component import queryUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from psj.content.interfaces import IExternalVocabConfig


def make_terms(strings):
    """Create zope.schema.SimpleTermss from strings.

    `strings` is expected to be a list of bytes in `utf-8` encoding.

    This function returns a list of `SimpleTerm` instances with
    unicode formatted titles and values and base 64 encoded tokens.

    `make_terms` guarantees that tokens are unique for each string put
    in and are representable as ASCII.
    """
    tuples = [(b64encode(s), s.decode('utf-8')) for s in strings]
    return [SimpleTerm(value=t[1], token=t[0], title=t[1])
            for t in tuples]


class InstitutesSourceBinder(object):
    """A source for institutes.

    We expect a named vocabulary factory registered as
    `psj.content.Institues` to lookup valid institute entries.

    The factory is looked up in the local site, therefore it should be
    registered there or globally.
    """
    grok.implements(IContextSourceBinder)

    def __call__(self, context):
        util = queryUtility(
            IExternalVocabConfig, name=u'psj.content.Institutes')
        if util is None:
            return SimpleVocabulary.fromValues([])
        path = util.get('path', None)
        if not path or not os.path.isfile(path):
            return SimpleVocabulary.fromValues([])
        return SimpleVocabulary(
            make_terms([line.strip() for line in open(path, 'r')]))


institutes_source = InstitutesSourceBinder()
