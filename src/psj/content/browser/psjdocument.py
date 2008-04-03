##
## psjdocument.py
## Login : <uli@pu.smp.net>
## Started on  Mon Mar 31 10:32:09 2008 Uli Fouquet
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
"""Views for PSJ documents.
"""
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class PSJDocumentView(BrowserView):
    """Default view of a PSJ document.
    """
    __call__ = ViewPageTemplateFile('psjdocument.pt')

    def getDocument(self):
        """Get the embedded document as HTML.
        """
        html = self.context.annotations['psj.content']['html']
        return html
    
