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
"""Public interfaces for psj.content.

"""
from zope.configuration.fields import Path
from zope.interface import Interface
from zope.schema import TextLine


class IExternalVocabConfig(Interface):
    """A vocabular configuration.

    Contains a path to a file where the vocabulary contents are
    stored in simple lines.

    See `zcml.py` for hints how to use this ZCML directive.

    `path` is the local path to a file containing vocabulary contents.

    `name` is the name under which the vocabulary is registered
    (globally).
    """
    path = Path(
        title=u'Path',
        description=u'Directory where a vocabulary file can be found.',
        required=True,
        )

    name = TextLine(
        title=u'Name',
        description=u'Name this vocab should be registered under.',
        required=True,
        )
