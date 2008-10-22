##
## extenders.py
## Login : <uli@pu.smp.net>
## Started on  Mon May 26 01:18:09 2008 Uli Fouquet
## $Id$
## 
## Copyright (C) 2008 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""
Schema extenders, that add metadata to existing types.
"""
from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import (StringWidget, BooleanWidget,
                                        ReferenceWidget, SelectionWidget,
                                        TextAreaWidget, MultiSelectionWidget,
                                        LinesWidget,)
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import (
    ReferenceBrowserWidget)
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content import folder
from Products.ATVocabularyManager import NamedVocabulary
from Products.CMFCore.utils import getToolByName
from psj.content.metadata.fields import (PSJTextLineField, PSJBooleanField,
                                         PSJRelationField, PSJLinesField,
                                         PSJTextField)
from psj.content.metadata.metadata import TextLineField as LineEntry
from psj.content.metadata.metadata import TextField as TextEntry
from psj.content.metadata.metadata import BooleanField as BoolEntry
from psj.content.metadata.metadata import RelationField as RelationEntry
from psj.content.metadata.metadata import VocabularyField as VocabularyEntry
from psj.content.metadata.metadata import LinesField as LinesEntry
from psj.content.interfaces import IBook, PSJ_TYPES, MEMBER_TYPES

class PageExtender(object):
    adapts(folder.ATFolder)
    implements(ISchemaExtender)


    fields = []

    def __init__(self, context):
        self.context = context

    def getFields(self):
        if not hasattr(self, 'md_reg'):
            try:
                self.md_reg = getToolByName(self.context,
                                            'metadataschemas_registry')
            except AttributeError:
                # This can happen during tests...
                return []
        md_schema = self.md_reg.getSchemaForObject(self.context)
        if md_schema is None:
            return []
        new_fields = []
        for key in md_schema:
            entry = md_schema.get(key)
            if isinstance(entry, TextEntry):
                new_fields.append(PSJTextLineField(
                    str('md_' + key),
                    schemata='metadata',
                    widget=TextAreaWidget(
                        label=entry.title,
                        description=entry.description)
                    ))
            elif isinstance(entry, LineEntry):
                new_fields.append(PSJTextLineField(
                    str('md_' + key),
                    schemata='metadata',
                    widget=StringWidget(
                        label=entry.title,
                        description=entry.description)
                    ))
            elif isinstance(entry, BoolEntry):
                new_fields.append(PSJBooleanField(
                    str('md_' + key),
                    schemata='metadata',
                    widget=BooleanWidget(
                        label=entry.title,
                        description=entry.description),
                    default = entry.default,
                    ))
            elif isinstance(entry, RelationEntry):
                new_fields.append(PSJRelationField(
                    str('md_'+key),
                    relationship = 'Rel_' + key,
                    multiValued = 1,
                    schemata='metadata',
                    isMetadata=1,
                    allowed_types = entry.allowed,
                    addable = True,
                    widget = ReferenceBrowserWidget(
                        destination = ".",
                        destination_types = entry.allowed,
                        label = entry.title,
                        description = entry.description,
                    ),
                    ))
            elif isinstance(entry, LinesEntry):
                if isinstance(entry.default, list):
                    default = tuple(entry.default)
                else:
                    default = entry.default
                new_fields.append(PSJLinesField(
                    str('md_'+key),
                    schemata='metadata',
                    isMetadata=1,
                    default = default,
                    widget = LinesWidget(
                        label = entry.title,
                        description = entry.description,
                    ),
                    ))
            elif isinstance(entry, VocabularyEntry):
                if entry.vocab is None:
                    continue
                if entry.multi is True:
                    widget = MultiSelectionWidget
                else:
                    widget = SelectionWidget

                new_fields.append(PSJLinesField(
                    str('md_'+key),
                    schemata = 'metadata',
                    widget = widget(
                        label = entry.title,
                        description = entry.description,
                        ),
                    vocabulary = NamedVocabulary(entry.vocab)
                    ))

        return new_fields

class BookExtender(PageExtender):
    """Books are not inherited from `Folder`.

    We need a specialized schema extender therefore.
    """
    adapts(IBook)
    implements(ISchemaExtender)


class FileTypeExtender(PageExtender):
    """An extender for ATFile based content types.

    This includes PSJFile and PSJPostPrint.
    """
    adapts(ATFile)
    implements(ISchemaExtender)

