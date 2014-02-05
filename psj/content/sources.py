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
"""Sources (in the zope.schema sense).

"""
from five import grok
from zope.component import queryUtility
from zope.schema.interfaces import (
    IContextSourceBinder, ISource, IVocabularyFactory,
    )
from zope.schema.vocabulary import SimpleVocabulary


@grok.implementer(IContextSourceBinder)
class institutes_source(object):
    """A source for institutes.

    We expect a named vocabulary registered as `psj.content.Institues`
    to lookup valid institute entries.
    """
    def __init__(self, context):
        self.context = context

    def __call__(self, context):
        vocab_factory = queryUtility(
            IVocabularyFactory, name=u'psj.content.Institutes', default=None)
        if vocab_factory is None:
            return SimpleVocabulary([])
        return vocab_factory()
