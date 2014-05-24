from setuptools import setup, find_packages
import os

version = '2.0dev'

tests_require = [
    'Pillow',
    'plone.app.testing',
    'plone.testing',
    'testing.redis',
    ]

setup(name='psj.content',
      version=version,
      description="Plone Scholarly Journal - the content types",
      long_description=open("README.md").read() + "\n" +
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
          'collective.autopermission',
          'grokcore.component',
          'plone.app.dexterity [grok, relations]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.app.textfield',
          'plone.behavior',             # for behaviours
          'plone.dexterity',
          'plone.directives.form',      # for behaviours
          'plone.formwidget.contenttree',
          'plone.formwidget.namedfile',  # for named files in behaviors
          'plone.namedfile[blobs]',      # for named files in behaviors
          'plone.supermodel',
          'z3c.relationfield',
          'zope.component',
          'zope.event',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.schema',
          'Products.ATVocabularyManager',
          'Products.FacultyStaffDirectory',
          'psj.policy',
          'redis',
          'ulif.openoffice',           # mention here to get scripts
      ],
      tests_require=tests_require,
      extras_require = {
          'test': tests_require,
          },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
