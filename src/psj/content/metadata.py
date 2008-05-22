##
## metadata.py
## Login : <uli@pu.smp.net>
## Started on  Thu May 22 14:02:35 2008 Uli Fouquet
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
Metadata for content objects.
"""

class Value(object):
    pass

class MetadataSet(object):
    data = dict()
    _keys = () # To keep an ordering, we maintain the keys in a tuple.
    index = 0

    def add(self, key, item):
        key = unicode(key)
        self.data[key] = item
        self._keys = self._keys + (key,)
        return

    def remove(self, key):
        key = unicode(key)
        del self.data[key]
        self._keys = tuple([x for x in list(self._keys) if x != key])
        return
    
    def __iter__(self):
        return self

    def next(self):
        if self.index < len(self._keys):
            self.index = self.index + 1
            return self._keys[self.index-1]
        self.index = 0
        raise StopIteration

    def get(self, key):
        return self.data[key]

