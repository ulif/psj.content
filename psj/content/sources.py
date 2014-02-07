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
from five import grok
from zope.component import queryUtility
from zope.schema.interfaces import (
    IContextSourceBinder, IVocabularyFactory,
    )
from zope.schema.vocabulary import SimpleVocabulary
from zope.component.interfaces import ComponentLookupError


class InstitutesSourceBinder(object):
    """A source for institutes.

    We expect a named vocabulary registered as `psj.content.Institues`
    to lookup valid institute entries.
    """
    grok.implements(IContextSourceBinder)

    def __call__(self, context):
        try:
            vocab_factory = queryUtility(
                IVocabularyFactory, name=u'psj.content.Institutes',
                context=context, default=None)
        except ComponentLookupError:
            # Certain contexts may cause this kind of error.
            # We retry lookup within the global registry then.
            vocab_factory = queryUtility(
                IVocabularyFactory, name=u'psj.content.Institutes',
                context=None, default=None)
        if vocab_factory is None:
            return SimpleVocabulary.fromValues([])
        return vocab_factory()


institutes_source = InstitutesSourceBinder()
