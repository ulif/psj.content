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
"""Dexterity base type for PSJ.

"""
from psj.content import _
from five import grok
from plone.dexterity.content import Container
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from psj.content.sources import institutes_source


class IBaseDoc(model.Schema):
    """A PSJ base.
    """
    psj_author = schema.List(
        title=_(u'Autor'),
        description=_(u'Autor(en) oder Herausgeber.'),
        required=False,
        readonly=True,
        value_type=schema.TextLine(),
        )

    psj_author_relation = RelationList(
        title=_(u'Autor Relation'),
        description=_(u'Autor oder Herausgeber. '),
        required=False,
        value_type=RelationChoice(
            title=_(
                u'Wählen Sie einen Personensatz aus Relation '
                u'zum Contenttype FSDPerson (Person)'),
            source=ObjPathSourceBinder(portal_type='FSDPerson')),
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

    psj_institute = schema.Choice(
        title=_(u'Institut'),
        description=_(u'Wählen Sie ein Institut aus der Options-Liste'),
        source=institutes_source,
        required=False,
        )


class BaseDoc(Container):
    """A PSJ document.
    """
    grok.implements(IBaseDoc)

    __allow_access_to_unprotected_subobjects__ = 1

    psj_author = FieldProperty(IBaseDoc["psj_author"])
    psj_author_relation = None
    psj_title = FieldProperty(IBaseDoc["psj_title"])
    psj_subtitle = FieldProperty(IBaseDoc["psj_subtitle"])
    psj_institute = FieldProperty(IBaseDoc["psj_institute"])
