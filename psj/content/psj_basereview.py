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
"""Dexterity base review type for PSJ.

"""
from psj.content import _
from five import grok
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from psj.content.sources import licenses_source
from psj.content.psj_basedoc import IBaseDoc, BaseDoc


class IBaseReview(IBaseDoc):
    """A PSJ review base.
    """
    psj_license = schema.Choice(
        title=_(u'Lizenz'),
        description=_(u'Wählen Sie eine Lizenz aus'),
        source=licenses_source,
        required=False,
        )


class BaseReview(BaseDoc):
    """A PSJ document.
    """
    grok.implements(IBaseReview)

    __allow_access_to_unprotected_subobjects__ = 1

    psj_author_relation = None
    psj_title = FieldProperty(IBaseReview["psj_title"])
    psj_subtitle = FieldProperty(IBaseReview["psj_subtitle"])
    psj_institute = FieldProperty(IBaseReview["psj_institute"])
    psj_license = FieldProperty(IBaseReview["psj_license"])
    psj_abstract = FieldProperty(IBaseReview["psj_abstract"])
    psj_doi = FieldProperty(IBaseReview["psj_doi"])
