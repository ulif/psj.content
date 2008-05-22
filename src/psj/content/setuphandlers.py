##
## setuphandlers.py
## Login : <uli@pu.smp.net>
## Started on  Thu May 22 18:37:11 2008 Uli Fouquet
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

# Setup the metadata schema registry

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def setupMetadataSchemaRegistry(context):
    """
    Setup MimetypesRegistry step.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('metadataschema-registry-various.txt') is None:
        return
    out = []
    site = context.getSite()
    #installMimetypesRegistry(site)
