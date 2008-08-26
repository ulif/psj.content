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
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from persistent.mapping import PersistentMapping

from Products.CMFCore.utils import registerToolInterface, UniqueObject
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


from zope.interface import implements

from psj.content.interfaces import IMetadataSchemaRegistryTool
from psj.content.interfaces import PSJ_TYPES, MEMBER_TYPES
from psj.content.metadata import MetadataSet

_www = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'browser')

class TypeMap(PersistentMapping):
    security = ClassSecurityInfo()
    security.declareObjectProtected(ManagePortal)

class MetadataSchemaRegistry(UniqueObject, ActionProviderBase, Folder):
    implements(IMetadataSchemaRegistryTool)
    security = ClassSecurityInfo()

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

    manage_addMetadataSchemaForm = PageTemplateFile('addMetadataSchema', _www)
    manage_main = PageTemplateFile('listMetadataSchemas', _www)
    manage_editMetadataSchemaForm = PageTemplateFile('editMetadataSchema',
                                                     _www)

    relation_targets = MEMBER_TYPES + PSJ_TYPES


    def __init__(self,):
        self._schemas = TypeMap()
        self._content_types = TypeMap()
        self._content_types['psjdocument'] = TypeMap(
            dotted_path='psj.content.content.psjdocument.PSJDocument',
            title='PSJ Document',
            schema=None)
        self._content_types['psjissue'] = TypeMap(
            dotted_path='psj.content.content.issue.PSJIssue',
            title='PSJ Issue',
            schema=None)
        self._content_types['psjvolume'] = TypeMap(
            dotted_path='psj.content.content.volume.PSJVolume',
            title='PSJ Volume',
            schema=None)
        self._content_types['psjmagazine'] = TypeMap(
            dotted_path='psj.content.content.magazine.PSJMagazine',
            title='PSJ Magazine',
            schema=None)
        self._content_types['psjbook'] = TypeMap(
            dotted_path='psj.content.content.book.PSJBook',
            title='PSJ Book',
            schema=None)
        self._content_types['psjretromagazine'] = TypeMap(
            dotted_path='psj.content.content.retromagazine.PSJRetroMagazine',
            title='PSJ Retro Magazine',
            schema=None)
        self._content_types['psjretroarticle'] = TypeMap(
            dotted_path='psj.content.content.retroarticle.PSJRetroArticle',
            title='PSJ Retro Article',
            schema=None)
        self._content_types['psjreview'] = TypeMap(
            dotted_path='psj.content.content.review.PSJReview',
            title='PSJ Review',
            schema=None)
        return

    def unregister(self, metadataset):
        id = metadataset.id
        del self._schemas[id]
        return

    security.declareProtected(ManagePortal, 'schemas')
    def schemas(self):
        return self._schemas

    security.declareProtected(ManagePortal, 'contentTypes')
    def contentTypes(self):
        return self._content_types

    security.declareProtected(ManagePortal, 'listSchemas')
    def listSchemas(self):
        return [str(schema) for schema in self.schemas()]

    security.declareProtected(ManagePortal, 'listContentTypes')
    def listContentTypes(self):
        return self._content_types.keys()

    security.declareProtected(ManagePortal, 'lookup')
    def lookup(self, id):
        return [self._schemas[x] for x in self._schemas.keys() if x == id]

    security.declareProtected(ManagePortal, 'lookupContentType')
    def lookupContentType(self, id):
        return self._content_types.get(id, None)

    security.declareProtected(ManagePortal, 'lookupContentTypeTitle')
    def lookupContentTypeTitle(self, id):
        return str(self.lookupContentType(id)['title'])

    def lookupContentTypesForSchema(self, id):
        result = [str(self.lookupContentType(x)['title'])
                  for x in self.getContentTypesForSchema(id)]
        return result

    security.declareProtected(ManagePortal, 'getSchemaForObject')
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
            
    security.declareProtected(ManagePortal, 'getContentTypesForSchema')
    def getContentTypesForSchema(self, schema_id):
        return [x for x in self._content_types.keys()
                if self._content_types[x]['schema'] == schema_id]

    security.declareProtected(ManagePortal, 'setContentTypesForSchema')
    def setContentTypesForSchema(self, objecttypes, schema_id):
        """Set schema as handler for the objecttypes.
        """
        # Delete old entries
        for objtype in self.getContentTypesForSchema(schema_id):
            new_type = self._content_types[objtype]
            new_type['schema'] = None
            self._content_types[objtype] = new_type

        for objtype in objecttypes:
            if objtype in self._content_types.keys():
                # Make sure the content type is placed so that the
                # persistence machinery gets updated.
                new_type = self._content_types[objtype]
                new_type['schema'] = schema_id
                self._content_types[objtype] = new_type
        return

    security.declareProtected(ManagePortal, 'manage_addMetadataSchema')
    def manage_addMetadataSchema(self, id, objecttypes, fields=(),
                                 REQUEST=None):
        try:
            mset = MetadataSet(id, fields)
            self._schemas[mset.id] = mset
            if isinstance(objecttypes, basestring):
                objecttypes = [objecttypes]
            self.setContentTypesForSchema(objecttypes, mset.id)
        except:
            # XXX Generate a log message here.
            pass
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')
        return

    def manage_delObjects(self, ids, REQUEST=None):
        """ delete the selected meta data schemata"""
        for id in ids:
            self.unregister(self.lookup(id)[0])
        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    def formDictToDict(self, formdict):
        """Transform a HTTP request dict into a real dict.
        """
        result = ()
        for elem in formdict:
            new_elem = dict()
            for attr in dir(elem):
                if attr.startswith('_'):
                    continue
                new_elem[attr] = elem[attr]
            result += (new_elem,)
        return result

    security.declareProtected(ManagePortal, 'process_addForm')
    def process_addForm(self, request, fields=[]):
        result = ()
        fields = request.form.get('fields', fields)
        del_fields = request.get('del_fields', None)
        objecttypes = request.form.get('objecttype', [])
        if isinstance(objecttypes, basestring):
            objecttypes = [objecttypes]
        num = -1
        for field in fields:
            num += 1
            if del_fields is not None:
                if request.form.get('del' + str(num), None) is not None:
                    continue
            result += (field,)
        result = dict(fields=result, objecttypes=objecttypes)
        if request.get('add_text_line', None) is not None:
            result['fields'] += ((
                dict(type='TextLine',
                     title=request.get('text_line.title', 'unnamed'),
                     default=request.get('text_line.default', None))),)
        if request.get('add_text', None) is not None:
            result['fields'] += ((
                dict(type='Text',
                     title=request.get('text.title', 'unnamed'),
                     default=request.get('text.default', None))),)
        if request.get('add_boolean', None) is not None:
            result['fields'] += ((
                dict(type='Boolean',
                     title=request.get('boolean.title', 'unnamed'),
                     default=request.get('boolean.default', False))),)
        if request.get('add_relation', None) is not None:
            allowed = tuple(request.get('relation.allowed',
                                        PSJ_TYPES+MEMBER_TYPES))
            if 'All' in allowed:
                allowed = PSJ_TYPES + MEMBER_TYPES
            if len(allowed) == 0:
                allowed = PSJ_TYPES + MEMBER_TYPES
            allowed = ','.join(allowed)
            result['fields'] += ((
                dict(type='Relation',
                     title=request.get('relation.title', 'unnamed'),
                     allowed=allowed,
                     )),)
        if request.get('add_vocab', None) is not None:
            result['fields'] += ((
                dict(type='Vocabulary',
                     title=request.get('vocab.title', 'unnamed'),
                     vocab=request.get('vocab.vocab', None)
                     )),)

        if request.get('add_schema', None) is not None:
            new_result = self.formDictToDict(result['fields'])
            name = request.get('id', 'Untitled Schema')
            self.manage_addMetadataSchema(name, objecttypes, new_result,
                                          REQUEST=request)
        return result

    def normalize_field(self, field):
        """Make sure, all fields have all attributes.

        Even those, that are used by other fields only. Otherwise we
        cannot use 'records' in the HTML form."""
        
        for attr in ['vocab', 'allowed', 'default']:
            if not attr in field.keys():
                field[attr] = None
        return field

    security.declareProtected(ManagePortal, 'manage_editMetadataSchema')
    def manage_editMetadataSchema(self, ms_id, name, objecttypes, fields=(),
                                  REQUEST=None):
        """Edit a meta data schema by id.
        """
        mset = self.lookup(ms_id)[0]
        mset = MetadataSet(name, fields)
        mset.id = ms_id
        self._schemas[mset.id] = mset
        self.setContentTypesForSchema(objecttypes, ms_id)

        if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

    def process_editForm(self, request):
        ms_id = request.form.get('ms_id', '')
        ms = self.lookup(ms_id)[0]
        old_name = ms.name
        old_fields = []
        if request.form.get('fields', None) is None:
            # populate edit form with already defined fields...
            old_fields = [ms.get(name).getDict() for name in ms]
        old_contenttypes = self.getContentTypesForSchema(ms_id)
        new_contenttypes = request.form.get('objecttype', [])
        if isinstance(new_contenttypes, basestring):
            new_contenttypes = [new_contenttypes]
        if len(new_contenttypes) == 0:
            new_contenttypes = old_contenttypes
        new_fields = self.process_addForm(request, fields=old_fields)['fields']
        new_name = request.form.get('name', old_name)
        result = dict(name = new_name, objecttypes = new_contenttypes,
                      fields = new_fields)
        if request.get('edit_schema', None) is not None:
            new_fields = self.formDictToDict(new_fields)
            self.manage_editMetadataSchema(ms_id, new_name, new_contenttypes,
                                           new_fields, REQUEST=request)
        return result

    def getRegisteredVocabularies(self):
        vocab_tool = getToolByName(self, 'portal_vocabularies')
        return vocab_tool.keys()

InitializeClass(MetadataSchemaRegistry)
registerToolInterface('metadataschemas_registry', IMetadataSchemaRegistryTool)
