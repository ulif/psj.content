##
## config.py
## Login : <uli@pu.smp.net>
## Started on  Sun Mar 30 17:20:15 2008 Uli Fouquet
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
"""Common configuration constants
"""

PROJECTNAME = "psj.content"

# This maps portal types to their corresponding add permissions.
# These are referenced in the root product __init__.py, during
# Archetypes/CMF type initialisation. The permissions here are
# also defined in content/configure.zcml, so that they can be
# looked up as a Zope 3-style IPermission utility.

# We prefix the permission names with our product name to group
# them sensibly. This is good practice, because it makes it
# easier to find permissions in the Security tab in the ZMI.

ADD_PERMISSIONS = {
    "PSJDocument"  : "PSJ: Add PSJ Document",
    "PSJIssue" : "PSJ: Add PSJ Issue",
    "PSJVolume" : "PSJ: Add PSJ Volume",
    "PSJMagazine" : "PSJ: Add PSJ Magazine",
    "PSJBook" : "PSJ: Add PSJ Book",
    "PSJRetroMagazine" : "PSJ: Add PSJ Retro Magazine",
    "PSJRetroArticle" : "PSJ: Add PSJ Retro Article",
    "PSJReview" : "PSJ: Add PSJ Review",
}
