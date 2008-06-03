##
## interfaces.py
## Login : <uli@pu.smp.net>
## Started on  Sun Mar 23 02:31:40 2008 Uli Fouquet
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
"""Interfaces for psj.content types.
"""

from zope.interface import Interface
from zope import schema

#from psj.content import PSJContentMessageFactory as _

class IDocument(Interface):
    """A PSJ document.
    """
    def rebuild():
        """This method is called, everytime a document is updated.
        """

class IIssue(Interface):
    """A PSJ issue.
    """
    def rebuild():
        """This method is called, everytime an issue is updated.
        """
    

class IMetadataItem(Interface):
    """An item in a metadata set.
    """

class IMetadataSet(Interface):
    """A set of metadata items.
    """
    def __iter__():
        """Make instances iterable.
        """

    def next():
        """Yield next element.
        """

    def add():
        """Add an metadata item.
        """

    def remove():
        """Remove an item.
        """
class IMetadataSchemaRegistryTool(Interface):
    """A registry for metadata schemas.
    """
