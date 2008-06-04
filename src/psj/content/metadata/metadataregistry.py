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
from Globals import InitializeClass, PersistentMapping
from Acquisition import aq_base

from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import implements

from psj.content.interfaces import IMetadataSchemaRegistryTool
from psj.content.metadata import MetadataSet

_www = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'browser')

class MetadataSchemaRegistry(UniqueObject, ActionProviderBase, Folder):
    implements(IMetadataSchemaRegistryTool)

    id = 'metadataschemas_registry'
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

    def __init__(self,):
        self._schemas = PersistentMapping()
        self._content_types = PersistentMapping()
        self._content_types['psjdocument'] = dict(
            dotted_path='psj.content.content.psjdocument.PSJDocument',
            title='PSJ Document',
            schema=None)
        self._content_types['psjissue'] = dict(
            dotted_path='psj.content.content.issue.PSJIssue',
            title='PSJ Issue',
            schema=None)
        self._content_types['psjvolume'] = dict(
            dotted_path='psj.content.content.volume.PSJVolume',
            title='PSJ Volume',
            schema=None)
        self._content_types['psjmagazine'] = dict(
            dotted_path='psj.content.content.volume.PSJMagazine',
            title='PSJ Magazine',
            schema=None)
        self._content_types['psjbook'] = dict(
            dotted_path='psj.content.content.volume.PSJBook',
            title='PSJ Book (review)',
            schema=None)
        return

    def unregister(self, metadataset):
        id = metadataset.id
        del self._schemas[id]
        return

    def schemas(self):
        return self._schemas

    def contentTypes(self):
        return self._content_types
        
    def listSchemas(self):
        return [str(schema) for schema in self.schemas()]

    def listContentTypes(self):
        return self._content_types.keys()

    def lookup(self, id):
        return [self._schemas[x] for x in self._schemas.keys() if x == id]

    def lookupContentType(self, id):
        return self._content_types.get(id, None)

    def getSchemaForObject(self, obj):
        dotted_path = None
        try:
            dotted_path = '%s.%s' % (obj.__module__,
                                     obj.__class__.__name__)
        except:
            return None
        ct = None
        for key, content_type in self._content_types.items():
            if content_type['dotted_path'] == dotted_path:
                schema_id = content_type['schema']
                return self._schemas.get(schema_id, None)
        return None
            

    def getContentTypesForSchema(self, schema_id):
        return [x for x in self._content_types.keys()
                if self._content_types[x]['schema'] == schema_id]

    def manage_addMetadataSchema(self, id, objecttype, fields=(),
                                 REQUEST=None):
        mset = MetadataSet(id, fields)
        self._schemas[mset.id] = mset
        if objecttype in self._content_types.keys():
            self._content_types[objecttype]['schema'] = mset.id
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')
        return

    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected meta data schemata"""
        for id in ids:
            self.unregister(self.lookup(id)[0])
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    def process_addForm(self, request):
        result = ()
        fields = request.form.get('fields', [])
        objecttype = request.form.get('objecttype', None)
        for field in fields:
            result += (field,)
        if request.get('add_text_line', None) is not None:
            result += ((dict(type='TextLine',
                            title=request.get('text_line.title', 'unnamed'),
                            default=request.get('text_line.default', None))),)
        if request.get('add_boolean', None) is not None:
            result += ((dict(type='Boolean',
                            title=request.get('boolean.title', 'unnamed'),
                            default=request.get('boolean.default', False))),)
        if request.get('add_schema', None) is not None:
            new_result = ()
            for elem in result:
                new_elem = dict()
                for attr in dir(elem):
                    if attr.startswith('_'):
                        continue
                    new_elem[attr] = elem[attr]
                new_result += (new_elem,)
            name = request.get('id', 'Untitled Schema')
            self.manage_addMetadataSchema(name, objecttype, new_result,
                                          REQUEST=request)
        return result


InitializeClass(MetadataSchemaRegistry)
registerToolInterface('metadataschemas_registry', IMetadataSchemaRegistryTool)
