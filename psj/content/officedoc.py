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
from BTrees.OOBTree import OOBTree
from psj.content import _
from five import grok
from plone.dexterity.content import Item, Container
from plone.directives.dexterity import DisplayForm
from plone.directives.form import fieldset, IFormFieldProvider
from plone.namedfile.field import NamedBlobFile as NamedBlobFileField
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.lifecycleevent.interfaces import IObjectAddedEvent


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

    psj_html_repr = NamedBlobFileField(
        title = _(u'HTML representation'),
        description = _(u'The HTML representation of the source document.'),
        required = False,
        readonly = True,
        )

    def psj_create_reprs():
        """Create PDF, HTML, etc. representations of source doc.
        """

class OfficeDoc(Container):
    """An office document.
    """
    grok.implements(IOfficeDoc)

    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, *args, **kw):
        super(OfficeDoc, self).__init__(*args, **kw)

    def psj_create_reprs(self):
        """Create PDF, HTML, etc. representations of source doc.
        """
        transforms = getToolByName(self, 'portal_transforms')
        in_data = self.psj_office_doc.data
        # create PDF
        out_data = transforms.convertTo(
            'application/pdf', in_data,
            mimetype='application/vnd.oasis.opendocument.text')
        if out_data is not None:
            # transform succeeded
            new_filename = self.psj_office_doc.filename + '.pdf'
            self.psj_pdf_repr = NamedBlobFile(
                data=out_data.getData(), filename=new_filename)
        # create HTML
        out_data = transforms.convertTo(
            'text/html', in_data,
            mimetype='application/vnd.oasis.opendocument.text')
        if out_data is not None:
            # transform succeeded
            new_filename = self.psj_office_doc.filename + '.html'
            html = out_data.getData()
            self.psj_html_repr = NamedBlobFile(
                data=html, filename=new_filename)
            for id, subdata in out_data.getSubObjects().items():
                id = id.decode('utf8')
                if id.lower()[-4:] in (u'.png', u'.jpg', u'.gif', u'.tif'):
                    new_id = self.invokeFactory('Image', id)
                else:
                    new_id = self.invokeFactory('File', id)
                new_context = self[new_id]
                new_context.update_data(subdata)
        return

    def SearchableText(self):
        """The text searchable in this document.

        Additionally to the regular fields (title, description, etc.),
        we take care for the HTML representation to be added to the
        searchable text.

        XXX: we should strip HTML markup before adding the text.
        """
        base_result = super(OfficeDoc, self).SearchableText()
        html_content = getattr(self.psj_html_repr, 'data', '')
        return '%s %s' % (base_result, html_content)


@grok.subscribe(IOfficeDoc, IObjectAddedEvent)
def create_representations(obj, event):
    """Event handler for freshly created IOfficeDocs.

    Creates PDF representation of uploaded office doc on creation.
    """
    obj.psj_create_reprs()
    return


class DisplayView(DisplayForm):
    """A display view for office docs.
    """
    grok.name('psj_view')
    grok.context(IOfficeDoc)
    grok.require('zope2.View')
