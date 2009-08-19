from setuptools import setup

PACKAGE = 'TracBacklog'
VERSION = '0.1'

setup(name=PACKAGE,
      version=VERSION,
      packages=['backlog'],
      package_data={
        'backlog': [
            'htdocs/css/*.css',
            'htdocs/img/*.png',
            'htdocs/js/*.js',
            'htdocs/js/dojo/*.js',
            'htdocs/js/dojo/dnd/*.js',
            'htdocs/js/dojo/date/*.js',
            'templates/*.html',
            'scripts/*'
        ]},
      entry_points='''
          [trac.plugins]
          backlog = backlog.web_ui
      ''')

