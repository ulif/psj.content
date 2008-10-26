##
## viewlets.py
## Login : <uli@pu.smp.net>
## Started on  Sat Oct 25 15:44:23 2008 Uli Fouquet
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
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.viewletmanager.manager import OrderedViewletManager
from psj.content.interfaces import IPSJDocumentMetadata

class PSJDocumentMetadataManager(OrderedViewletManager):
    """A viewlet manager that displays metadata.
    """
    pass

class PSJDocumentMetadataViewlet(BrowserView):
    """A viewlet that renders a metadata box for documents.
    """
    __call__ = ViewPageTemplateFile('metadatabox.pt')

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(PSJDocumentMetadataViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.manager = manager
    
    def render(self, *args, **kw):
        return self.__call__(*args, **kw)
    
    def getFields(self):
        """Get a list of dicts describing metadatafields.

        Each dict of the list provides the keywords of the appropriate
        metadataset entry. But only the following ones are used:

        - `id`: the ID of the field, i.e. the attribute name

        - `description`: the textual description of the field

        - `isregularfield`: True for real ATfields only.

        - `value`: a replacement value, in case a field is not part of
          the object or cannot be rendered in some other respect.
        """
        schemata_reg = getToolByName(self.context, 'metadataschemas_registry')
        schema_fields = schemata_reg.getSchemaForObject(self.context)
        if schema_fields is None:
            # No fields to render...
            return []
        
        # Build a dict of fields we expect...
        schema_result = []
        # We use `list()` here to get the fields in the appropriate order.
        for field_id in list(schema_fields):
            field = schema_fields[field_id]
            field = field.getDict()
            field.update(id = 'md_%s' % field_id)
            field.update(value = u'') # Default, if the value cannot be found
            field.update(isregularfield = False)
            schema_result.append(field)

        # Now pull in the values from the real object, if they
        # exist. We don't want to display attributes, that are (yet)
        # not provided by the object nor attributes, that are not part
        # of the approriate metadata schemadefinition (i.e. such, that
        # are not part of the schema any more).
        result = []        
        if not hasattr(self.context, 'Schemata'):
            return schema_result
        if not 'metadata' in self.context.Schemata().keys():
            return schema_result
        obj_fields = self.context.Schemata()['metadata']
        for field in schema_result:
            if field['id'] not in obj_fields.keys():
                result.append(field)
                continue
            field.update(value = field['id'])
            field.update(isregularfield = True)
            result.append(field)
        return result

    def checkPermission(self, *args, **kw):
        """Check whether an action is allowed on an object.

        This is only needed, because reference browser widget requires
        a checkPermission function, that is not available by default.
        """
        # XXX: This is a lie...
        return True

    def getPortal(self):
        """Return the portal object.

        This is required by reference browser widget only.
        """
        return self.context.portal_url.getPortalObject()
