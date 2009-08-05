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
            'templates/*.html',
            'scripts/*'
        ]},
      entry_points='''
          [trac.plugins]
          backlog = backlog.web_ui
      ''')

