from setuptools import setup
import backlog

PACKAGE = 'TracBacklog'

setup(name=PACKAGE,
      version=backlog.get_version(),
      packages=['backlog'],
      package_data={
        'backlog': [
            'htdocs/css/*.css',
            'htdocs/img/*.png',
            'htdocs/js/*.js',
            'htdocs/js/dojo/*.js',
            'htdocs/js/dojo/dnd/*.js',
            'htdocs/js/dojo/date/*.js',
            'htdocs/js/dojo/fx/*.js',
            'templates/*.html',
        ]},
      entry_points={
          'trac.plugins': [
              'backlog = backlog.web_ui',
              'backlog_prefs = backlog.prefs',
          ]
      },
      install_requires=[
        'simplejson>=2.0',
        ],
      author="John Szakmeister",
      author_email="john@szakmeister.net",
      description="Enables Trac to be used for managing your ticket backlog.",
      long_description='''
Provides ticket backlog management in Trac.  It allows users to use
drag-and-drop in their web browser to reorder tickets, and to assign tickets
to a milestone.
''',
      url="https://github.com/jszakmeister/trac-backlog",
      license="Simplified BSD",
      )

