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
"""Dexterity type for office docs.

"""
from psj.content import _
from five import grok
from plone.dexterity.content import Item
from plone.directives.form import fieldset, IFormFieldProvider
from plone.namedfile.field import NamedBlobFile as NamedBlobFileField
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from zope import schema


class IOfficeDoc(model.Schema):
    """An office document.
    """
    model.fieldset(
        'psj_docholder',
        label = _(u'Office Documents'),
        fields = ('psj_office_doc', 'psj_pdf_repr'),
        )

    psj_office_doc = NamedBlobFileField(
        title = _(u'Source Office File (.doc, .docx, .odt)'),
        description = _(u'Source Document'),
        required = True,
        )

    psj_pdf_repr = NamedBlobFileField(
        title = _(u'PDF version'),
        description = _(u'The PDF representation of the source document.'),
        required = False,
        readonly = True,
        )


class OfficeDoc(Item):
    """An office document.
    """
    grok.implements(IOfficeDoc)
