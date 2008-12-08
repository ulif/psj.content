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

If you want to run this package alone, follow the follwing steps:

1) Run `bootstrap.py`::

     $ python2.4 bootstrap/bootstrap.py

   This will create basic build scripts and directories.

2) Run `buildout`::

     $ ./bin/buildout

   This will fetch all packages needed from the internet and install
   it locally. Also all scripts are created by this step.

3) Start the server::

     $ ./bin/instance fg

   Now you can login on http://localhost:8080/manage. Default
   credentials are: username ``admin``, password ``admin``.

   You can change the credentials in ``buildout.cfg``.

   If you want to start the server in background, do::

     $ ./bin/instance start

4) Stop the server by pressing CTRL-C on the commandline. If you
   started the server in background, do::


     $ ./bin/instance stop

If you want to run the tests:

5) Do the tests::

     $ ./bin/instance test -s psj.content

