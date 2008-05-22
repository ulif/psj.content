##
## metadataregistry.py
## Login : <uli@pu.smp.net>
## Started on  Thu May 22 18:00:57 2008 Uli Fouquet
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
import os
from OFS.Folder import Folder
from Globals import InitializeClass

from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements

from psj.content.interfaces import IMetadataSchemaRegistryTool

_www = os.path.join(os.path.dirname(__file__), 'www')

class MetadataSchemaRegistry(UniqueObject, ActionProviderBase, Folder):
    implements(IMetadataSchemaRegistryTool)

    id = 'metadataschema_registry'
    meta_type = 'MetadataSchema Registry'
    isPrincipiaFolderish = 1 # Show in the ZMI

    meta_types = all_meta_types = (
        {'name' : 'MetadataSchema',
         'action' : 'manage_addMetadataSchema'},
        )

    manage_options = (
        ( { 'label' : 'MetadataSchemas',
            'action' : 'manage_main'},) +
        Folder.manage_options[2:]
        )

    manage_addMimeTypeForm = PageTemplateFile('addMetadataSchema', _www)
    manage_main = PageTemplateFile('listMetadataSchemas', _www)
    manage_editMimeTypeForm = PageTemplateFile('editMetadataSchema', _www)

    #security = ClassSecurityInfo()
    

InitializeClass(MetadataSchemaRegistry)
registerToolInterface('metadataschema_registry', IMetadataSchemaRegistryTool)
