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
from psj.content import _
from psj.content.interfaces import IExternalVocabConfig


def make_terms(strings):
    """Create zope.schema.SimpleTermss from strings.

    `strings` is expected to be a list of bytes in `utf-8` encoding.

    This function returns a list of `SimpleTerm` instances with
    unicode formatted titles and values and base 64 encoded tokens.

    `make_terms` guarantees that tokens are unique for each string put
    in and are representable as ASCII.
    """
    tuples = [(b64encode(s), _(s.decode('utf-8'))) for s in strings if s]
    return [SimpleTerm(value=t[1], token=t[0], title=t[1])
            for t in tuples]


class ExternalVocabBinder(object):
    """A source retrieving data from an external vocabulary.

    We expect some IExternalVocabConfig registered under name `name`.

    This binder is initialized with a `name` under which we will look
    up IExternalVocabConfigs when binding.

    When an instance of this binder is called for the first time, it
    tries to find the appropriate external vocab config, tries to read
    the file linked to the config and returns a SimpleVocabulary.

    If one of these steps fails (the external vocab was not
    registered, the path given in a config does not exist, etc.), we
    return an empty vocabulary.
    """
    grok.implements(IContextSourceBinder)

    name = None
    vocab = None

    def __init__(self, name):
        self.name = name

    def __call__(self, context):
        if self.vocab is not None:
            return self.vocab
        util = queryUtility(IExternalVocabConfig, name=self.name)
        if util is None:
            return SimpleVocabulary.fromValues([])
        path = util.get('path', None)
        if not path or not os.path.isfile(path):
            return SimpleVocabulary.fromValues([])
        self.vocab = SimpleVocabulary(
            make_terms([line.strip() for line in open(path, 'r')]))
        return self.vocab


institutes_source = ExternalVocabBinder(u'psj.content.Institutes')
licenses_source = ExternalVocabBinder(u'psj.content.Licenses')
publishers_source = ExternalVocabBinder(u'psj.content.Publishers')
subjectgroup_source = ExternalVocabBinder(u'psj.content.Subjectgroup')
ddcgeo_source = ExternalVocabBinder(u'psj.content.DDCGeo')
ddcsach_source = ExternalVocabBinder(u'psj.content.DDCSach')
