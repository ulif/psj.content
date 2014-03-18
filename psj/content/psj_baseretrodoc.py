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
"""Dexterity base type for PSJ retro docs.

"""
from psj.content import _
from five import grok
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.component import queryUtility
from zope.schema.fieldproperty import FieldProperty
from psj.content.interfaces import ISearchableTextGetter
from psj.content.sources import institutes_source, licenses_source


class IBaseRetroDoc(model.Schema):
    """A PSJ base.
    """
    psj_author = schema.List(
        title=_(u'Autor'),
        description=_(u'Autor(en) oder Herausgeber.'),
        required=False,
        value_type=schema.TextLine(),
        )

    psj_title = schema.TextLine(
        title=_(u'Titel'),
        description=_(u'Titel der Publikation'),
        required=True,
        )

    psj_subtitle = schema.TextLine(
        title=_(u'Untertitel'),
        description=_(u'Untertitel der Publikation'),
        required=False,
        )

    psj_pages = schema.TextLine(
        title=_(u'Seiten'),
        description=_(u'Seiten von bis'),
        required=False,
        )

    psj_institute = schema.List(
        title=_(u'Institut'),
        description=_(u'Wählen Sie ein Institut aus'),
        value_type=schema.Choice(
            title=_(u'Institut'),
            description=_(u'Institut'),
            source=institutes_source,
            required=False,
            ),
        required=False,
        )

    psj_license = schema.Choice(
            title=_(u'Lizenz'),
            description=_(u'Wählen Sie eine Lizenz aus'),
            source=licenses_source,
            required=False,
        )

    psj_abstract = RichText(
        title=_(u'Abstract'),
        description=_(u'Inhaltliche Zusammenfassung'),
        default_mime_type="text/html",
        output_mime_type="text/html",
        allowed_mime_types=('text/structured', 'text/plain', 'text/html'),
        default=u'',
        required=False,
        )

    psj_doi = schema.TextLine(
        title=_(u'DOI'),
        description=_(u'Digital Object Identifier'),
        required=True,
        )


class BaseRetroDoc(Container):
    """A PSJ document.
    """
    grok.implements(IBaseRetroDoc)

    __allow_access_to_unprotected_subobjects__ = 1

    psj_author = FieldProperty(IBaseRetroDoc["psj_author"])
    psj_title = FieldProperty(IBaseRetroDoc["psj_title"])
    psj_subtitle = FieldProperty(IBaseRetroDoc["psj_subtitle"])
    psj_pages = FieldProperty(IBaseRetroDoc["psj_pages"])
    psj_institute = FieldProperty(IBaseRetroDoc["psj_institute"])
    psj_license = FieldProperty(IBaseRetroDoc["psj_license"])
    psj_abstract = FieldProperty(IBaseRetroDoc["psj_abstract"])
    psj_doi = FieldProperty(IBaseRetroDoc["psj_doi"])

    def SearchableText(self):
        """The text searchable in this document.

        Additionally to the regular fields (title, description, etc.),
        we take care for the PSJ specific fields to be added to the
        searchable text.
        """
        base_result = super(BaseRetroDoc, self).SearchableText()
        text_getter = queryUtility(ISearchableTextGetter)
        psj_attribs_text = ''
        if text_getter is not None:
            psj_attribs_text = text_getter(context=self)
        return '%s %s' % (base_result, psj_attribs_text)
