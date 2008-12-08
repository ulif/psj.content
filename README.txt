Introduction
************


The ``Plone Scholarly Journal`` (PSJ) is a collection of packages to
create and maintain scholarly journals using Plone.

The special abilities of PSJ are:

 * High quality on-the-fly transformations of office documents using
   OpenOffice.org.

 * Flexible metadata handling

This package contains the content types and metadata handling.

Currently, the whole thing consists of three packages:

 * ``psj.content`` (this package)

 * ``psj.policy`` (provides mainly office-document transformations using
   OpenOffice.org)

 * ``psj.site`` (kind of umbrella package for the other packages).


Requirements
============

PSJ runs on Plone 3.x with Python 2.4.

Installation
============

If you want to run a complete PSJ site, then you should use
``psj.site``, which will fetch all other needed packages
automatically. ``psj.site`` comes also with extended installation
notes.

The whole installation process is driven by ``zc.buildout``.

