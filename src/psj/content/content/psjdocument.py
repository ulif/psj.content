##
## psjdocument.py
## Login : <uli@pu.smp.net>
## Started on  Sun Mar 30 16:58:02 2008 Uli Fouquet
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
Definition of PSJ document type.
"""
import re

from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from BTrees.OOBTree import OOBTree
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName

from psj.content.interfaces import IDocument
from psj.content.config import PROJECTNAME
from psj.content import PSJContentMessageFactory as _

PSJDocumentSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.FileField(
        'document',
        required=False,
        searchable=True,
        primary=True,
        widget=atapi.FileWidget(
            label=_(u'Document'),
            description=_(u'Upload an office document here'))
       ),
    atapi.FileField(
        'pdfdocument',
        required=False,
        seachable=False,
        primary=False,
        ),
    ))

# Switch default attributes storage to annotation (instead attribute)
PSJDocumentSchema['title'].storage = atapi.AnnotationStorage()
PSJDocumentSchema['description'].storage = atapi.AnnotationStorage()
PSJDocumentSchema['document'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(PSJDocumentSchema, folderish=True, moveDiscussion=False)

class _Replacer(object):

    def __init__(self, sublist, instance):
        self.sublist = sublist
        self.instance = instance

    def __call__(self, match):
        prefix = match.group(1)
        inside = match.group(2)
        postfix = match.group(3)
        # patch inside
        if inside.startswith('./'):
            # some .swt are converted with this prefix
            inside = inside[2:]
        if inside in self.sublist:
            # convert elems that are known images
            inside = '%s/%s' % (
                self.instance.getId(), inside)
        result = '<img%s src="%s"%s>' % (prefix, inside, postfix)
        return result




class PSJDocument(folder.ATFolder):
    """A PSJ document.
    """
    implements(IDocument)

    portal_type = 'PSJDocument'
    _at_rename_after_creation = True
    schema = PSJDocumentSchema
    annotations_key = 'psj.content'
    _re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]=' +
                            '"([^">]*)"([^>]*)>')


    def _initDocAnnotations(self):
        """Create the private annotations.

        In the `psj.content` annotation we store the subobjects of an
        office documents like images etc. Furthermore we store the
        HTML transformation there, so, that is must be generated only
        on major changes.
        """
        annotations = IAnnotations(self)
        # Create our private annotations store, if it doesn't exist yet...
        if not self.annotations_key in annotations.keys():
            annotations[self.annotations_key] = OOBTree()
        if not 'html' in annotations[self.annotations_key].keys():
            annotations[self.annotations_key]['html'] = None
        if not 'pdf' in annotations[self.annotations_key].keys():
            annotations[self.annotations_key]['pdf'] = None
        if not 'subobjects' in annotations[self.annotations_key].keys():
            annotations[self.annotations_key]['subobjects'] = OOBTree()
        self.annotations = annotations
        return

    def clearSubObjects(self):
        """Delete all subobjects from local annotation.
        """
        for elem in self.keys():
            del self[elem]
        return

    def setSubObject(self, id, data):
        """Add a subobjects in our annotations.
        """
        at_file = ATFile(id)
        at_file.update_data(data)
        self[id] = at_file
        return

    def _getSubObject(self, id, request=None, response=None):
        """Get a subobject. This is not working at the moment.
        """
        if id in self.annotations[self.annotations_key]['subobjects'].keys():
            return self.annotations[self.annotations_key]['subobjects'][id]
        else:
            raise AttributeError

    def setHtml(self, data):
        """Set the HTML transformation of the office document stored.
        """
        self.annotations[self.annotations_key]['html'] = data
        self.reindexObject()
        return

    def getHtml(self):
        """Get the current HTML representation of the document.
        """
        return self.annotations[self.annotations_key]['html']

    def setPdf(self, data):
        """Set the PDF transformation of the office document stored.
        """
        self.annotations[self.annotations_key]['pdf'] = data
        return

    def getPdf(self):
        """Get the current PDF represenatation of the document.
        """
        return self.annotations[self.annotations_key]['pdf']

    def rebuild(self):
        """Convert local document to HTML and store it.

        XXX this should be interruptible because conversion can be
            rather time consuming.

        XXX create a log message.

        """
        self._initDocAnnotations()
        self.clearSubObjects()

        transforms = getToolByName(self, 'portal_transforms')
        raw_file = self['document']
        if raw_file.filename == '':
            self.setHtml(u'')
            self.setPdf('')
            return

        # Create HTML representation...
        data = transforms.convertTo('text/html', str(raw_file.data),
                                    filename=raw_file.filename)
        if data is None:
            self.setHtml(u'')
            return

        html = data.getData()
        html = re.sub('\xef\x81\xac', "", html)
        subobjs = data.getSubObjects()

        if len(subobjs) > 0:
            for id, data in subobjs.items():
                self.setSubObject(id, data)
            html = self._re_imgsrc.sub(_Replacer(subobjs.keys(), self), html)
        self.setHtml(html.decode('utf-8'))

        # Create PDF/A representation...
        data = transforms.convertTo('application/pdf', str(raw_file.data),
                                    filename=raw_file.filename)
        if data is None:
            self.setPdf(u'')
            return
        pdf = data.getData()
        self.setPdf(pdf)
        return
        
        
atapi.registerType(PSJDocument, PROJECTNAME)
