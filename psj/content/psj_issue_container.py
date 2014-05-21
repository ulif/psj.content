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
"""Dexterity issue container type for PSJ.

"""
from psj.content import _
from five import grok
from plone.dexterity.content import Container
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.component import queryUtility
from zope.schema.fieldproperty import FieldProperty
from psj.content.interfaces import ISearchableTextGetter


class IPSJIssueContainer(model.Schema):
    """A PSJ base.
    """
    psj_author = schema.List(
        title=_(u'Autor'),
        description=_(u'Autor(en) oder Herausgeber.'),
        required=True,
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

    psj_publication_year = schema.TextLine(
        title=_(u'Ersterscheinungsdatum'),
        description=_(u'Ersterscheinungsdatum der Publikation'),
        required=True,
        )

    psj_issue_number = schema.TextLine(
        title=_(u'Nr.'),
        description=_(u''),
        required=True,
        )


class PSJIssueContainer(Container):
    """A PSJ issue container.
    """
    grok.implements(IPSJIssueContainer)

    __allow_access_to_unprotected_subobjects__ = 1

    @property
    def psj_author(self):
        """Get persons from `psj_author_relation` as list of strings.
        """
        if self.psj_author_relation is None:
            return []
        persons = [rel.to_object for rel in self.psj_author_relation]
        return [p.Title().decode('utf-8') for p in persons]

    psj_author_relation = None
    psj_title = FieldProperty(IPSJIssueContainer["psj_title"])
    psj_subtitle = FieldProperty(IPSJIssueContainer["psj_subtitle"])
    psj_publication_year = FieldProperty(
        IPSJIssueContainer["psj_publication_year"])
    psj_issue_number = FieldProperty(IPSJIssueContainer["psj_issue_number"])


    def SearchableText(self):
        """The text searchable in this document.

        Additionally to the regular fields (title, description, etc.),
        we take care for the PSJ specific fields to be added to the
        searchable text.
        """
        base_result = super(PSJIssueContainer, self).SearchableText()
        text_getter = queryUtility(ISearchableTextGetter)
        psj_attribs_text = ''
        if text_getter is not None:
            psj_attribs_text = text_getter(context=self)
        return '%s %s' % (base_result, psj_attribs_text)
