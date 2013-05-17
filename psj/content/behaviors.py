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
from plone.namedfile.field import NamedBlobFile
from zope.component import adapts
from zope.interface import implements, alsoProvides
from zope.schema import TextLine, Text
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

class IPSJBehavior(Schema):
    """A behavior supporting PSJ content types.
    """

class IPSJAuthor(IPSJBehavior):
    """A document author.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('psj_author',),
        )

    psj_author = TextLine(
        title = _(u'Author'),
        description = _(u'Document Author'),
        required = False,
        )

alsoProvides(IPSJAuthor, IFormFieldProvider)

class IPSJTitle(IPSJBehavior):
    """A document title.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('psj_title',),
        )

    psj_title = TextLine(
        title = _(u'Title'),
        description = _(u'Document Title'),
        required = False,
        )

alsoProvides(IPSJTitle, IFormFieldProvider)

class IPSJSubtitle(IPSJBehavior):
    """A document subtitle.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('psj_subtitle',),
        )

    psj_subtitle = TextLine(
        title = _(u'Subtitle'),
        description = _(u'Document Subtitle'),
        required = False,
        )

alsoProvides(IPSJSubtitle, IFormFieldProvider)

class IPSJAbstract(IPSJBehavior):
    """A document abstract.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('psj_abstract',),
        )

    psj_abstract = Text(
        title = _(u'Abstract'),
        description = _(u'Document Abstract'),
        required = False,
        )

alsoProvides(IPSJAbstract, IFormFieldProvider)


class IPSJBaseData(IPSJBehavior):
    """Document base metadata, including authorname, title, etc.
    """
    fieldset(
        'psj_metadata',
        label = _(u'PSJ Metadata'),
        fields = ('psj_author', 'psj_title', 'psj_subtitle', 'psj_abstract'),
        )

    psj_author = IPSJAuthor['psj_author']
    psj_title = IPSJTitle['psj_title']
    psj_subtitle = IPSJSubtitle['psj_subtitle']
    psj_abstract = IPSJAbstract['psj_abstract']

alsoProvides(IPSJBaseData, IFormFieldProvider)


class IPSJOfficeDocTransformer(IPSJBehavior):
    """A document that provides some office doc.

    The transformer also supports automatic transforms of uploaded
    office docs.
    """
    fieldset(
        'psj_docholder',
        label = _(u'Office Docs'),
        fields = ('psj_office_doc',),
        )

    psj_office_doc = NamedBlobFile(
        title = _(u'Source Office File (.doc, .docx, .odt)'),
        description = _(u'Document Abstract'),
        required = True,
        )

alsoProvides(IPSJOfficeDocTransformer, IFormFieldProvider)


class PSJAuthor(PSJMetadataBase):
    """A behaviour allowing to set the author of a PSJ document.
    """
    implements(IPSJAuthor)

    psj_author = DCFieldProperty(
        IPSJAuthor['psj_author'],
        get_name = 'psj_author'
        )


class PSJTitle(PSJMetadataBase):
    """A behaviour allowing to set the title of a PSJ document.
    """
    implements(IPSJTitle)

    psj_title = DCFieldProperty(
        IPSJTitle['psj_title'],
        get_name = 'psj_title'
        )

class PSJSubtitle(PSJMetadataBase):
    """A behaviour allowing to set the subtitle of a PSJ document.
    """
    implements(IPSJSubtitle)

    psj_subtitle = DCFieldProperty(
        IPSJSubtitle['psj_subtitle'],
        get_name = 'psj_subtitle'
        )

class PSJAbstract(PSJMetadataBase):
    """A behaviour allowing to set the abstract of a PSJ document.
    """
    implements(IPSJAbstract)

    psj_abstract = DCFieldProperty(
        IPSJAbstract['psj_abstract'],
        get_name = 'psj_abstract'
        )

class PSJBaseData(PSJAuthor, PSJTitle, PSJSubtitle, PSJAbstract):
    """A behavior providing base metadata.
    """
    implements(IPSJBaseData)

class PSJOfficeDocTransformer(PSJMetadataBase):
    """A document that provides some office doc.
    """
    implements(IPSJOfficeDocTransformer)

    psj_office_doc = DCFieldProperty(
        IPSJOfficeDocTransformer['psj_office_doc'],
        get_name = 'psj_office_doc',
        )
