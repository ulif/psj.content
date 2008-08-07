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
from psj.content.util import get_id_string
from persistent.mapping import PersistentMapping
from persistent import Persistent

class MetadataSet(PersistentMapping):
    data = dict()
    _keys = () # To keep an ordering, we maintain the keys in a tuple.
    index = 0

    def __init__(self, name=u'Unnamed', fields=()):
        super(MetadataSet, self).__init__()
        self.data = dict()
        id = get_id_string(name)
        self.id = id
        if not isinstance(name, unicode):
            name = unicode(name, 'utf-8')
        self.name = name
        for field in fields:
            ftype = field.get('type', None)
            ftitle = field.get('title')
            del field['type']
            del field['title']
            item = None
            if ftype == 'TextLine':
                item = TextLineField(ftitle, **field)
            if ftype == 'Boolean':
                item = BooleanField(ftitle, **field)
            if ftype == 'Relation':
                item = RelationField(ftitle, **field)
            if ftype == 'Vocabulary':
                item = RelationField(ftitle, **field)
            if item is None:
                continue
            self.add(item)
        return

    def add(self, item):
        key = item.id
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

    def get(self, key, default=None):
        if key in self.data.keys():
            return self.data[key]
        return default


class BaseField(object):

    def __init__(self, title):
        self.title = unicode(title)
        self.id = get_id_string(self.title)
        return

class BooleanField(object):

    default = False

    def __init__(self, title, **kw):
        self.title = unicode(title)
        self.id = get_id_string(self.title)
        self.default = kw.get('default', False)
        return

    def getDict(self):
        return dict(
            title = self.title,
            id = self.id,
            default = self.default,
            type = 'Boolean',)

class TextLineField(object):

    default = None

    def __init__(self, title, **kw):
        self.title = unicode(title)
        self.id = get_id_string(self.title)
        default = kw.get('default', None)
        if default is not None:
            self.default = unicode(default)
        return

    def getDict(self):
        return dict(
            title = self.title,
            id = self.id,
            default = self.default,
            type = 'TextLine',)
    
class RelationField(BaseField):

    def __init__(self, title, **kw):
        self.title = unicode(title)
        self.id = get_id_string(self.title)

    def getDict(self):
        return dict(
            title = self.title,
            id = self.id,
            type = 'Relation',)


class VocabularyField(BaseField):

    def __init__(self, title, **kw):
        self.title = unicode(title)
        self.id = get_id_string(self.title)
        self.vocab = kw.get('vocab', None)

    def getDict(self):
        return dict(
            title = self.title,
            id = self.id,
            vocab = self.vocab,
            type = 'Vocabulary',)
