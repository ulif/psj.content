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
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName


# See: http://developer.plone.org/reference_manuals/external/plone.app.dexterity/advanced/vocabularies.html
@grok.provider(IContextSourceBinder)
def institutes_source(context):
    atvm = getToolByName(context, 'portal_vocabularies', default=None)
    # see https://github.com/collective/Products.ATVocabularyManager/blob/master/Products/ATVocabularyManager/tests/testATVocabularyManager.py
    if atvm is None:
        return SimpleVocabulary()
    return SimpleVocabulary()
