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
"""Plone Behaviors for `psj.content`.

"""
from five import grok
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.dexterity.interfaces import IDexterityContent
from plone.directives.form import (
    Schema, fieldset, IFormFieldProvider, mode, primary)
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobFile as NamedBlobFileField
from plone.namedfile.file import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.component import adapts, queryUtility
from zope.interface import implements, alsoProvides
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.schema import TextLine, Text, Choice, List
from psj.content import _
from psj.content.interfaces import IRedisStoreConfig
from psj.content.sources import (
    publishers_source, subjectgroup_source, ddcgeo_source, ddcsach_source,
    ddczeit_source, RedisSource,
    )
from psj.content.psj_basedoc import IBaseDoc, BaseDoc

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
        label=_(u'PSJ Metadata'),
        fields=('psj_author', ),
        )

    psj_author = TextLine(
        title=_(u'Author'),
        description=_(u'Document Author'),
        required=False,
        )

alsoProvides(IPSJAuthor, IFormFieldProvider)


class IPSJTitle(IPSJBehavior):
    """A document title.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_title',),
        )

    psj_title = TextLine(
        title=_(u'Title'),
        description=_(u'Document Title'),
        required=False,
        )

alsoProvides(IPSJTitle, IFormFieldProvider)


class IPSJSubtitle(IPSJBehavior):
    """A document subtitle.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_subtitle',),
        )

    psj_subtitle = TextLine(
        title=_(u'Subtitle'),
        description=_(u'Document Subtitle'),
        required=False,
        )

alsoProvides(IPSJSubtitle, IFormFieldProvider)


class IPSJAbstract(IPSJBehavior):
    """A document abstract.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_abstract',),
        )

    psj_abstract = Text(
        title=_(u'Abstract'),
        description=_(u'Document Abstract'),
        required=False,
        )

alsoProvides(IPSJAbstract, IFormFieldProvider)


class IPSJContributors(IPSJBehavior):
    """FSDPersons as contributors.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_contributors',),
        )

    psj_contributors = RelationList(
        title=_(u'Beitragende'),
        description=_(u'Contributors'),
        required=False,
        value_type=RelationChoice(
            title=_(
                u'Wählen Sie einen Personensatz aus Relation '
                u'zum Contenttype FSDPerson (Person)'),
            source=ObjPathSourceBinder(portal_type='FSDPerson')),
        )


alsoProvides(IPSJContributors, IFormFieldProvider)


class IPSJBaseData(IPSJBehavior):
    """Document base metadata, including authorname, title, etc.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_author', 'psj_author_relation', 'psj_title', 'psj_subtitle', 'psj_institute', 'psj_license', 'psj_abstract', 'psj_doi'),
        )

    psj_author = IBaseDoc['psj_author']
    psj_author_relation = IBaseDoc['psj_author_relation']
    psj_title = IBaseDoc['psj_title']
    psj_subtitle = IBaseDoc['psj_subtitle']
    psj_institute = IBaseDoc['psj_institute']
    psj_license = IBaseDoc['psj_license']
    psj_abstract = IPSJAbstract['psj_abstract']
    psj_doi = IBaseDoc['psj_doi']

alsoProvides(IPSJBaseData, IFormFieldProvider)


class IPSJAddRetro(IPSJBehavior):
    """Technical metadata for retro articles and postprints.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_link_bsb', 'psj_ocr_text', 'psj_file'),
        )

    psj_link_bsb = TextLine(
        title=_(u'Link BSB'),
        description=_(u'Link zum Bereitstellungssystem der BSB'),
        required=False,
        )

    psj_ocr_text = Text(
        title=_(u'OCR Text'),
        description=_(u''),
        required=False,
        )

    primary('psj_file')
    psj_file = NamedBlobFileField(
        title=_(u'Digitized document'),
        description=_(u'Digitized document'),
        required=False,
        )

    mode(psj_ocr_text='input')


alsoProvides(IPSJAddRetro, IFormFieldProvider)


class IPSJPartOf(IPSJBehavior):
    """The meta data fields used to describe things being parts of others.
    """
    psj_series = TextLine(
        title=_(u'Reihe'),
        description=_(u'Reihentitel'),
        required=False,
        )

    psj_volume = TextLine(
        title=_(u'Band'),
        description=_(u'Band'),
        required=False,
        )


alsoProvides(IPSJPartOf, IFormFieldProvider)


class IPSJEdition(IPSJBehavior):
    """The meta data fields to describe an edition.
    """
    psj_publisher = Choice(
        title=_(u'Verlag'),
        description=u'',
        source=publishers_source,
        required=False,
        )

    psj_isbn_issn = TextLine(
        title=_(u'ISBN/ISSN'),
        description=u'',
        required=False,
        )

    psj_publication_year = TextLine(
        title=_(u'Erscheinungsjahr'),
        description=u'',
        required=False,
        )


alsoProvides(IPSJEdition, IFormFieldProvider)


class IPSJSubjectIndexing(IPSJBehavior):
    """Fields to categorize some document.
    """
    fieldset(
        'psj_metadata',
        label=_(u'PSJ Metadata'),
        fields=('psj_subject_group',
                'psj_ddc_geo',
                'psj_ddc_sach',
                'psj_ddc_zeit',
                'psj_gnd_id',
                'psj_gnd_terms',
                'psj_free_keywords',
                ),
        )

    psj_subject_group = List(
        title=_(u'Epochenkategorie'),
        description=_(u''),
        value_type=Choice(
            title=_(u'Kategorie'),
            description=_(u''),
            source=subjectgroup_source,
            required=False,
            ),
        required=False,
        )

    psj_ddc_geo = List(
        title=_(u'Land/Region'),
        description=_(u''),
        value_type=Choice(
            title=_(u'Geo-Kategorie'),
            description=_(u''),
            source=ddcgeo_source,
            required=False,
            ),
        required=False,
        )

    psj_ddc_sach = List(
        title=_(u'Sach-Klassifikation'),
        description=_(u''),
        value_type=Choice(
            title=_(u'Sach-Kategorie'),
            description=_(u''),
            source=ddcsach_source,
            required=False,
            ),
        required=False,
        )

    psj_ddc_zeit = List(
        title=_(u'Epoche'),
        description=_(u''),
        value_type=Choice(
            title=_(u'Zeit-Kategorie nach DDC'),
            description=_(u''),
            source=ddczeit_source,
            required=False,
            ),
        required=False,
        )

    psj_gnd_id = List(
        title=_(u'Identnummern aus GND'),
        description=_(u''),
        value_type=TextLine(
            title=_(u'Identnummer'),
            description=_(u''),
            required=True,
            ),
        required=False,
        )

    psj_gnd_terms = List(
        title=_(u'GND Schlagwörter'),
        description=_(u''),
        value_type=TextLine(
            title=_(u'GND Schlagwort'),
            description=_(u''),
            ),
        required=False,
        readonly=True,
        )

    psj_free_keywords = List(
        title=_(u'Freie Schlagwörter'),
        description=_(u''),
        value_type=TextLine(
            title=_(u'Freies Schlagwort'),
            description=_(u''),
            ),
        required=False,
        )


alsoProvides(IPSJSubjectIndexing, IFormFieldProvider)


class IPSJRelatedContent(IPSJBehavior):
    """Some related document.
    """
    fieldset(
        'psj_related_content',
        label=_(u'Related Content'),
        fields=('psj_media', 'psj_primary_source'),
        )

    psj_media = TextLine(
        title=_(u'Media'),
        description=_(u'Link to folder with images or videos. '
                      u'Presented as tab'),
        required=True,
        )

    psj_primary_source = TextLine(
        title=_(u'Quellen'),
        description=_(u'Link to related source on other site.'),
        required=True,
        )


alsoProvides(IPSJRelatedContent, IFormFieldProvider)


class IPSJOfficeDocTransformer(IPSJBehavior):
    """A document that provides some office doc.

    The transformer also supports automatic transforms of uploaded
    office docs.
    """
    fieldset(
        'psj_docholder',
        label=_(u'Office Docs'),
        fields=('psj_office_doc', 'psj_pdf_repr'),
        )

    primary('psj_office_doc')
    psj_office_doc = NamedBlobFileField(
        title=_(u'Source Office File (.doc, .docx, .odt)'),
        description=_(u'Document Abstract'),
        required=True,
        )

    psj_pdf_repr = NamedBlobFileField(
        title=_(u'PDF version'),
        description=_(u'The PDF representation of the source document.'),
        required=False,
        readonly=True,
        )


alsoProvides(IPSJOfficeDocTransformer, IFormFieldProvider)


class PSJAuthor(PSJMetadataBase):
    """A behaviour allowing to set the author of a PSJ document.
    """
    implements(IPSJAuthor)

    psj_author = DCFieldProperty(
        IPSJAuthor['psj_author'],
        get_name='psj_author'
        )


class PSJTitle(PSJMetadataBase):
    """A behaviour allowing to set the title of a PSJ document.
    """
    implements(IPSJTitle)

    psj_title = DCFieldProperty(
        IPSJTitle['psj_title'],
        get_name='psj_title'
        )


class PSJSubtitle(PSJMetadataBase):
    """A behaviour allowing to set the subtitle of a PSJ document.
    """
    implements(IPSJSubtitle)

    psj_subtitle = DCFieldProperty(
        IPSJSubtitle['psj_subtitle'],
        get_name='psj_subtitle'
        )


class PSJAbstract(PSJMetadataBase):
    """A behaviour allowing to set the abstract of a PSJ document.
    """
    implements(IPSJAbstract)

    psj_abstract = DCFieldProperty(
        IPSJAbstract['psj_abstract'],
        get_name='psj_abstract'
        )


class PSJContributors(PSJMetadataBase):
    """A behaviour allowing to set FSD persons as contributors.
    """
    implements(IPSJContributors)

    psj_abstract = DCFieldProperty(
        IPSJContributors['psj_contributors'],
        get_name='psj_contributors'
        )


class PSJBaseData(BaseDoc):
    """A behavior providing base metadata.
    """
    implements(IBaseDoc)


class PSJAddRetro(PSJMetadataBase):
    """A behavior providing technical metadata for retro docs.
    """
    implements(IPSJAddRetro)

    psj_link_bsb = DCFieldProperty(
        IPSJAddRetro['psj_link_bsb'],
        get_name='psj_link_bsb'
        )

    psj_ocr_text = DCFieldProperty(
        IPSJAddRetro['psj_ocr_text'],
        get_name='psj_ocr_text'
        )

    primary('psj_file')
    psj_file = DCFieldProperty(
        IPSJAddRetro['psj_file'],
        get_name='psj_file'
        )

class PSJPartOf(PSJMetadataBase):
    """A behavior providing fields for docs being part of others.
    """
    implements(IPSJPartOf)

    psj_series = DCFieldProperty(
        IPSJPartOf['psj_series'],
        get_name='psj_series'
        )

    psj_volume = DCFieldProperty(
        IPSJPartOf['psj_volume'],
        get_name='psj_volume'
        )


class PSJEdition(PSJMetadataBase):
    """A behavior providing fields for edited documents.
    """
    implements(IPSJEdition)

    psj_publisher = DCFieldProperty(
        IPSJEdition['psj_publisher'],
        get_name='psj_publisher'
        )

    psj_isbn_issn = DCFieldProperty(
        IPSJEdition['psj_isbn_issn'],
        get_name='psj_isbn_issn'
        )

    psj_publication_year = DCFieldProperty(
        IPSJEdition['psj_publication_year'],
        get_name='psj_publication_year'
        )


class PSJOfficeDocTransformer(PSJMetadataBase):
    """A document that provides some office doc.
    """
    implements(IPSJOfficeDocTransformer)

    psj_office_doc = DCFieldProperty(
        IPSJOfficeDocTransformer['psj_office_doc'],
        get_name='psj_office_doc',
        )

    psj_pdf_repr = DCFieldProperty(
        IPSJOfficeDocTransformer['psj_pdf_repr'],
        get_name='psj_pdf_repr',
        )


@grok.subscribe(IPSJOfficeDocTransformer, IObjectCreatedEvent)
def create_representations(transformer, event):
    """Event handler for freshly created IPSJOfficeDocTransforms.

    Creates PDF representation of uploaded office doc on creation.
    """
    transforms = getToolByName(transformer, 'portal_transforms')
    if transformer.psj_office_doc:
        in_data = transformer.psj_office_doc.data
    else:
        return
    out_data = transforms.convertTo(
        'application/pdf', in_data,
        mimetype='application/vnd.oasis.opendocument.text')
    if out_data is None:
        # transform failed
        return
    new_filename = transformer.psj_office_doc.filename + '.pdf'
    transformer.psj_pdf_repr = NamedBlobFile(
        data=out_data.getData(), filename=new_filename)

@grok.subscribe(IPSJOfficeDocTransformer, IObjectCreatedEvent)
def psj_create_html(transformer, event):
    """Create an HTML representation of `in_data`.

    `in_data` is supposed to be the binary content of an office
    document.

    `transforms` are the portal transforms.
    """
    transforms = getToolByName(transformer, 'portal_transforms')
    if transformer.psj_office_doc:    
        in_data = transformer.psj_office_doc.data
    else:
        return

    out_data = transforms.convertTo(
        'text/html', in_data,
        mimetype='application/vnd.oasis.opendocument.text')
    if out_data is None:
        # transform failed
        return
    new_filename = transformer.psj_office_doc.filename + '.html'
    html = out_data.getData()
    transformer.psj_html_repr = NamedBlobFile(
        data=html, filename=new_filename)
    # for name in transformer.keys():
    #     # make sure all old extra-files (images, etc.) are
    #     # deleted.
    #     del transformer[name]
    # for name, subdata in out_data.getSubObjects().items():
    #     name = name.decode('utf8')
    #     if name.lower()[-4:] in (u'.png', u'.jpg', u'.gif', u'.tif'):
    #         new_name = transformer.invokeFactory('Image', name)
    #     else:
    #         new_name = transformer.invokeFactory('File', name)
    #     new_context = transformer[new_name]
    #     new_context.update_data(subdata)


class PSJSubjectIndexing(PSJMetadataBase):
    """A behavior providing fields for subject indexing.
    """
    implements(IPSJSubjectIndexing)

    psj_subject_group = DCFieldProperty(
        IPSJSubjectIndexing['psj_subject_group'],
        get_name='psj_subject_group',
        )

    psj_ddc_geo = DCFieldProperty(
        IPSJSubjectIndexing['psj_ddc_geo'],
        get_name='psj_ddc_geo',
        )

    psj_ddc_sach = DCFieldProperty(
        IPSJSubjectIndexing['psj_ddc_sach'],
        get_name='psj_ddc_sach',
        )

    psj_ddc_zeit = DCFieldProperty(
        IPSJSubjectIndexing['psj_ddc_zeit'],
        get_name='psj_ddc_zeit',
        )

    psj_gnd_id = DCFieldProperty(
        IPSJSubjectIndexing['psj_gnd_id'],
        get_name='psj_gnd_id',
        )

    psj_free_keywords = DCFieldProperty(
        IPSJSubjectIndexing['psj_free_keywords'],
        get_name='psj_free_keywords',
        )

    @property
    def psj_gnd_terms(self):
        if not hasattr(self, 'psj_gnd_id'):
            return []
        conf = queryUtility(IRedisStoreConfig, name="psj.content.redis-GND")
        if conf is None:
            return []
        redis_source = RedisSource(
            host=conf['host'], port=conf['port'], db=conf['db'])
        result = []
        for elem in self.psj_gnd_id:
            try:
                val = redis_source.getTerm(elem)
                result.append(val.title)
            except LookupError:
                # id not in store.
                result.append(elem)
        return result


class PSJRelatedContent(PSJMetadataBase):
    """A behavior providing fields for related content.
    """
    implements(IPSJRelatedContent)

    psj_media = DCFieldProperty(
        IPSJRelatedContent['psj_media'],
        get_name='psj_media'
        )

    psj_primary_source = DCFieldProperty(
        IPSJRelatedContent['psj_primary_source'],
        get_name='psj_primary_source'
        )
