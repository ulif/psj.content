##
## retroarticle.py
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
Definition of PSJ retro article.
"""
import os
import re
import StringIO

from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from BTrees.OOBTree import OOBTree
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName

from psj.content.interfaces import IReview
from psj.content.config import PROJECTNAME
from psj.content import PSJContentMessageFactory as _
from psj.content.content.psjdocument import PSJDocument, PSJDocumentSchema

ReviewSchema = PSJDocumentSchema.copy()

# Switch default attributes storage to annotation (instead attribute)
ReviewSchema['title'].storage = atapi.AnnotationStorage()
ReviewSchema['description'].storage = atapi.AnnotationStorage()
ReviewSchema['document'].storage = atapi.AnnotationStorage()
ReviewSchema['pdfdocument'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(ReviewSchema, folderish=True, moveDiscussion=False)

class PSJReview(PSJDocument):
    """A retro article.
    """
    implements(IReview)

    portal_type = 'PSJReview'
    _at_rename_after_creation = True
    schema = ReviewSchema
    annotations_key = 'psj.content'
    _re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]=' +
                            '"([^">]*)"([^>]*)>')

atapi.registerType(PSJReview, PROJECTNAME)
