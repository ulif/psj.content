##
## file.py
## Login : <uli@pu.smp.net>
## Started on  Wed Oct 22 08:36:11 2008 Uli Fouquet
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
Definition of PSJ File type.
"""
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from psj.content.interfaces import IFile
from psj.content.config import PROJECTNAME

PSJFileSchema = ATFileSchema.copy()

finalizeATCTSchema(PSJFileSchema, folderish=False, moveDiscussion=False)

class PSJFile(ATFile):
    """A PSJ file.
    """
    implements(IFile)
    portal_type = 'PSJFile'
    schema = PSJFileSchema

    def rebuild(self):
        pass
    
atapi.registerType(PSJFile, PROJECTNAME)
