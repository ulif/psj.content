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
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


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

    def psj_create_reprs():
        """Create PDF, HTML, etc. representations of source doc.
        """


class OfficeDoc(Item):
    """An office document.
    """
    grok.implements(IOfficeDoc)

    def psj_create_reprs(self):
        """Create PDF, HTML, etc. representations of source doc.
        """
        transforms = getToolByName(self, 'portal_transforms')
        in_data = self.psj_office_doc.data
        out_data = transforms.convertTo(
        'application/pdf', in_data,
        mimetype='application/vnd.oasis.opendocument.text')
        if out_data is None:
            # transform failed
            return
        new_filename = self.psj_office_doc.filename + '.pdf'
        self.psj_pdf_repr = NamedBlobFile(
            data=out_data.getData(), filename=new_filename)


@grok.subscribe(IOfficeDoc, IObjectCreatedEvent)
def create_representations(obj, event):
    """Event handler for freshly created IOfficeDocs.

    Creates PDF representation of uploaded office doc on creation.
    """
    obj.psj_create_reprs()
    return
