# -*- coding: utf-8 -*-
#  psj.content is copyright (c) 2014 Uli Fouquet
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
"""Utilities and helpers for PSJ.

"""
from five import grok
from psj.content.interfaces import ISearchableTextGetter

#: The attributes considered to hold fulltext.
FULLTEXT_ATTRIBUTES = (
    'psj_author', 'psj_title', 'psj_subtitle', 'psj_institute',
    'psj_abstract', 'psj_publication_year', 'psj_ocr_text', 'psj_series',
    'psj_publisher', 'psj_subject_group', 'psj_ddc_geo', 'psj_ddc_geo',
    'psj_ddc_sach', 'psj_ddc_zeit', 'psj_gnd_term', 'psj_free_keywords',
    'psj_contributors'
    )


def to_string(text):
    """Turn `text` into a string.

    Unicode texts are converted via `encode()`, other objects are
    simply casted by `str()`.
    """
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    elif not isinstance(text, str):
        text = str(text)
    return text


class SearchableTextGetter(grok.GlobalUtility):
    """A utility extracting searchable text from objects.

    For PSJ objects we want a bunch of attribute values to be
    searchable by simple full-text search. The `SearchableTextGetter`
    scans object instances for these attributes and tries to turn the
    values into strings. Also `list` and `tuple` values are supported.

    An instance of this class is available as an unnamed global
    utility at runtime.
    """

    grok.implements(ISearchableTextGetter)

    def __call__(self, context):
        """Search all `FULLTEXT_ATTRIBUTES` in `context`.

        Values of `context` attributes are searched and turned into a
        single string.
        """
        result = ''
        for attr_name in FULLTEXT_ATTRIBUTES:
            attr_val = getattr(context, attr_name, None)
            if not attr_val:
                continue
            if isinstance(attr_val, list) or isinstance(attr_val, tuple):
                attr_val = ' '.join([to_string(x.strip()) for x in attr_val])
            else:
                attr_val = to_string(attr_val)
            attr_val = attr_val.replace('\n', ' ')
            result = '%s %s' % (result, attr_val.strip())
        return result.strip()
