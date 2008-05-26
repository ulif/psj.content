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
from Products.Archetypes.public import StringWidget, BooleanWidget
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content import folder
from psj.content.metadata.fields import PSJTextLineField, PSJBooleanField

class PageExtender(object):
    adapts(folder.ATFolder)
    implements(ISchemaExtender)


    fields = [
        PSJBooleanField(
            "super_power",
            schemata='metadata',
            widget = BooleanWidget(label="This page has super powers")
            ),
        PSJTextLineField(
            "some_text",
            schemata='metadata',
            widget = StringWidget(label="Enter text or so")
            ),
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
