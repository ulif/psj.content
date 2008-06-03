##
## volume.py
## Login : <uli@pu.smp.net>
## Started on  Tue Jun  3 23:53:36 2008 Uli Fouquet
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
An Volume of a Magazine.
"""
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from psj.content.interfaces import IVolume
from psj.content.config import PROJECTNAME
from psj.content import PSJContentMessageFactory as _


PSJVolumeSchema = folder.ATFolderSchema.copy()

PSJVolumeSchema['title'].storage = atapi.AnnotationStorage()
PSJVolumeSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(PSJVolumeSchema, folderish=True, moveDiscussion=False)

class PSJVolume(folder.ATFolder):
    implements(IVolume)

    portal_type = 'PSJVolume'
    _at_rename_after_creation = True
    schema = PSJVolumeSchema
    annotations_key = 'psj.content'

    def rebuild(self):
        pass

atapi.registerType(PSJVolume, PROJECTNAME)

