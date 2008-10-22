##
## postprint.py
## Login : <uli@pu.smp.net>
## Started on  Wed Oct 22 13:37:00 2008 Uli Fouquet
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
Definition of PSJ PostPrint type.
"""
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from psj.content.interfaces import IPostPrint
from psj.content.config import PROJECTNAME

PSJPostPrintSchema = ATFileSchema.copy()

finalizeATCTSchema(PSJPostPrintSchema, folderish=False, moveDiscussion=False)

class PSJPostPrint(ATFile):
    """A PostPrint document.
    """
    implements(IPostPrint)
    portal_type = 'PSJPostPrint'
    schema = PSJPostPrintSchema

    def rebuild(self):
        pass
    
atapi.registerType(PSJPostPrint, PROJECTNAME)
