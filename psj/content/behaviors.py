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
"""Plone Behaviors for `psj.content`.

"""
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.dexterity.interfaces import IDexterityContent
from plone.directives.form import Schema, fieldset, IFormFieldProvider
from zope.component import adapts
from zope.interface import implements, alsoProvides
from zope.schema import TextLine
from psj.content import _

class PSJMetadataBase(object):
    """An adapter storing metadata directly on an object using the
    standard CMF DefaultDublinCoreImpl getters and setters.

    `context` is the object to be adapted.
    """
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

class PSJFieldProperty(DCFieldProperty):
    """A PSJ field property.

    A DC field property for PSJ behaviors.
    """
    pass

class IAuthor(Schema):
    """A document author.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('author',),
        )

    author = TextLine(
        title = _(u'Author'),
        description = _(u'Document Author'),
        required = False,
        )

alsoProvides(IAuthor, IFormFieldProvider)

class Author(PSJMetadataBase):
    """A behaviour allowing to set the author of a PSJ document.
    """
    implements(IAuthor)

    author = DCFieldProperty(
        IAuthor['author'],
        get_name = 'author'
        )
