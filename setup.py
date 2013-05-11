from setuptools import setup, find_packages
import os

version = '2.0dev'

setup(name='psj.content',
      version=version,
      description="Plone Scholarly Journal - the content types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='zope psj plone3 scholar journal plone',
      author='Uli Fouquet',
      author_email='uli@gnufix.de',
      url='http://pypi.python.org/pypi/psj.content',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['psj'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Plone',
          'plone.app.dexterity',
          'collective.autopermission',
          'grokcore.component',
          'plone.behavior',            # for behaviours
          'plone.directives.form',      # for behaviours
          'zope.i18nmessageid',
          'plone.dexterity',
          'zope.component',
          'zope.interface',
          'zope.schema',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
