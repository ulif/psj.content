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
import md5
from five import grok
from plone.dexterity.content import Container
from plone.directives.dexterity import DisplayForm
from plone.namedfile.field import NamedBlobFile as NamedBlobFileField
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.component import queryUtility
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectModifiedEvent
    )
from psj.content import _
from psj.content.interfaces import ISearchableTextGetter


class IOfficeDoc(model.Schema):
    """An office document.
    """
    model.fieldset(
        'psj_docholder',
        label=_(u'Office Documents'),
        fields=('psj_office_doc', 'psj_pdf_repr'),
        )

    psj_office_doc = NamedBlobFileField(
        title=_(u'Source Office File (.doc, .docx, .odt)'),
        description=_(u'Source Document'),
        required=True,
        )

    psj_md5 = schema.ASCIILine(
        title=_(u'MD5 of Source'),
        description=_(u'The MD5 sum of the contained office doc.'),
        required=False,
        readonly=True,
        )

    psj_pdf_repr = NamedBlobFileField(
        title=_(u'PDF version'),
        description=_(u'The PDF representation of the source document.'),
        required=False,
        readonly=True,
        )

    psj_html_repr = NamedBlobFileField(
        title=_(u'HTML representation'),
        description=_(u'The HTML representation of the source document.'),
        required=False,
        readonly=True,
        )

    def psj_create_reprs():
        """Create PDF, HTML, etc. representations of source doc.
        """


class OfficeDoc(Container):
    """An office document.
    """
    grok.implements(IOfficeDoc)

    __allow_access_to_unprotected_subobjects__ = 1

    psj_office_doc = None
    psj_md5 = None
    psj_html_repr = None
    psj_pdf_repr = None

    def psj_create_pdf(self, transforms, in_data):
        """Create a PDF representation of `in_data`.

        `in_data` is supposed to be the binary content of an office
        document.

        `transforms` are the portal transforms.
        """
        out_data = transforms.convertTo(
            'application/pdf', in_data,
            mimetype='application/vnd.oasis.opendocument.text')
        if out_data is None:
            # transform failed
            return
        new_filename = self.psj_office_doc.filename + '.pdf'
        self.psj_pdf_repr = NamedBlobFile(
            data=out_data.getData(), filename=new_filename)

    def psj_create_html(self, transforms, in_data):
        """Create an HTML representation of `in_data`.

        `in_data` is supposed to be the binary content of an office
        document.

        `transforms` are the portal transforms.
        """
        out_data = transforms.convertTo(
            'text/html', in_data,
            mimetype='application/vnd.oasis.opendocument.text')
        self.psj_md5 = md5.new(in_data).hexdigest()
        if out_data is None:
            # transform failed
            return
        new_filename = self.psj_office_doc.filename + '.html'
        html = out_data.getData()
        self.psj_html_repr = NamedBlobFile(
            data=html, filename=new_filename)
        for name in self.keys():
            # make sure all old extra-files (images, etc.) are
            # deleted.
            del self[name]
        for name, subdata in out_data.getSubObjects().items():
            name = name.decode('utf8')
            if name.lower()[-4:] in (u'.png', u'.jpg', u'.gif', u'.tif'):
                new_name = self.invokeFactory('Image', name)
            else:
                new_name = self.invokeFactory('File', name)
            new_context = self[new_name]
            new_context.update_data(subdata)

    def psj_create_reprs(self):
        """Create PDF, HTML, etc. representations of source doc.
        """
        transforms = getToolByName(self, 'portal_transforms')
        in_data = getattr(self.psj_office_doc, 'data', None)
        if in_data is not None:  # safety belt
            self.psj_create_pdf(transforms, in_data)
            self.psj_create_html(transforms, in_data)
        return

    def SearchableText(self):
        """The text searchable in this document.

        Additionally to the regular fields (title, description, etc.),
        we take care for the PSJ specific fields to be added to the
        searchable text.
        """
        base_result = super(OfficeDoc, self).SearchableText()
        text_getter = queryUtility(ISearchableTextGetter)
        psj_attribs_text = ''
        if text_getter is not None:
            psj_attribs_text = text_getter(context=self)
        return '%s %s' % (base_result, psj_attribs_text)


@grok.subscribe(IOfficeDoc, IObjectAddedEvent)
def create_representations(obj, event):
    """Event handler for freshly created IOfficeDocs.

    Creates PDF representation of uploaded office doc on creation.
    """
    obj.psj_create_reprs()
    return


@grok.subscribe(IOfficeDoc, IObjectModifiedEvent)
def update_representations(obj, event):
    """Event handler for modified IOfficeDocs.

    Checks, whether source doc was really changed (by comparing MD5
    sums) and if so updates all respective representations.
    """
    md5_sum = md5.new(getattr(obj.psj_office_doc, 'data', '')).hexdigest()
    old_md5 = getattr(obj, 'psj_md5', '')
    if md5_sum == old_md5:
        return
    obj.psj_create_reprs()
    return


class DisplayView(DisplayForm):
    """A display view for office docs.
    """
    grok.name('psj_view')
    grok.context(IOfficeDoc)
    grok.require('zope2.View')
