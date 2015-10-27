# -*- coding: utf-8 -*-
#  psj.content is copyright (c) 2014, 2015 Uli Fouquet
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#  MA 02111-1307 USA.
#
"""Sources (in the zope.schema sense) and source context binders.

"""
import os
import redis
from five import grok
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import queryUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from psj.content.interfaces import IExternalVocabConfig, IRedisStoreConfig
from psj.content.utils import make_terms, tokenize, untokenize


class ExternalVocabBinder(object):
    """A source retrieving data from an external vocabulary.

    We expect some IExternalVocabConfig registered under name `name`.

    This binder is initialized with a `name` under which we will look
    up IExternalVocabConfigs when binding.

    When an instance of this binder is called for the first time, it
    tries to find the appropriate external vocab config, tries to read
    the file linked to the config and returns a SimpleVocabulary.

    If one of these steps fails (the external vocab was not
    registered, the path given in a config does not exist, etc.), we
    return an empty vocabulary.
    """
    grok.implements(IContextSourceBinder)

    name = None
    vocab = None

    def __init__(self, name):
        self.name = name

    def __call__(self, context):
        if self.vocab is not None:
            return self.vocab
        util = queryUtility(IExternalVocabConfig, name=self.name)
        if util is None:
            return SimpleVocabulary.fromValues([])
        path = util.get('path', None)
        if not path or not os.path.isfile(path):
            return SimpleVocabulary.fromValues([])
        self.vocab = SimpleVocabulary(
            make_terms([line.strip() for line in open(path, 'r')]))
        return self.vocab


class ExternalRedisBinder(ExternalVocabBinder):
    """A source that looks up an external REDIS store to retrieve
    valid entries.
    """
    def __call__(self, context):
        if self.vocab is not None:
            return self.vocab
        util = queryUtility(IRedisStoreConfig, name=self.name)
        if util is None:
            return SimpleVocabulary.fromValues([])
        return RedisSource(
            host=util['host'], port=util['port'], db=util['db'])


class RedisSource(object):
    """A zope.schema ISource containing values from a Redis Store.

    This source contains keys of a Redis Store db.
    """
    grok.implements(IQuerySource)

    _client = None

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def _get_client(self):
        if self._client is None:
            # create a client as late as possible but keep it then
            self._client = redis.StrictRedis(
                host=self.host, port=self.port, db=self.db)
        return self._client

    def __contains__(self, value):
        result = self._get_client().get(value)
        return result is not None

    def getTerm(self, value):
        """Return the ITerm object for term `value`.

        Raises `LookupError` if no such value can be found in Redis
        Store.

        Returns ITerm of `value`, where `value` is expected to be an
        existing *key* in a Redis store.

        The `title` of any resulting term will be set to the
        corresponding `value`.
        """
        db_val = self._get_client().get(value)
        if db_val is None:
            raise LookupError('No such term: %s' % value)
        return SimpleTerm(
            value, token=tokenize(value), title=db_val.decode('utf-8'))

    def __iter__(self):
        """Required by IIterableVocabulary.

        Return an iterator over all elements in source.
        """
        client = self._get_client()
        for key in client.scan_iter():
            value = self._get_client().get(key)
            yield SimpleTerm(
                key, token=tokenize(key), title=value.decode('utf-8'))

    def __len__(self):
        """Required by IIterableVocabulary.
        """
        return self._get_client().dbsize()

    def getTermByToken(self, token):
        key = untokenize(token)
        return self.getTerm(key)

    def search(self, query_string):
        """Return an iterable of ITerms matching `query_string`.

        A term matches, if its title starts with `query_string`.
        """
        for term in self:
            if term.title.startswith(query_string):
                yield term


class RedisKeysSource(RedisSource):
    """A redis source that only looks for keys in Redis stores.
    """
    def getTerm(self, value):
        result = super(RedisKeysSource, self).getTerm(value)
        return SimpleTerm(
            result.value, token=result.token, title=result.value)


class RedisAutocompleteSource(RedisSource):
    """A redis source that supports autocomplete functionality.

    `zset_name` sets the name of the redis ZSET containing the
    autocomplete terms.

    `separator` tells how we separate normalized terms from
    non-normalized when we lookup entries in redis ZSET.
    """
    def __init__(self, host='localhost', port=6379, db=0,
                 zset_name="autocomplete", separator="&&"):
        self.host = host
        self.port = port
        self.db = db
        self.zset_name = zset_name
        self.separator = separator

    def __contains__(self, value):
        search_term = "[%s%s" % (value, self.separator)
        if isinstance(search_term, unicode):
            search_term = search_term.encode("utf-8")
        result = self._get_client().zlexcount(
            self.zset_name, search_term, search_term + chr(255))
        return result and True or False


language_source = ExternalVocabBinder(u'psj.content.Languages')
institutes_source = ExternalVocabBinder(u'psj.content.Institutes')
licenses_source = ExternalVocabBinder(u'psj.content.Licenses')
publishers_source = ExternalVocabBinder(u'psj.content.Publishers')
subjectgroup_source = ExternalVocabBinder(u'psj.content.Subjectgroup')
ddcgeo_source = ExternalVocabBinder(u'psj.content.DDCGeo')
ddcsach_source = ExternalVocabBinder(u'psj.content.DDCSach')
ddczeit_source = ExternalVocabBinder(u'psj.content.DDCZeit')
gndid_source = ExternalVocabBinder(u'psj.content.GND_ID')
