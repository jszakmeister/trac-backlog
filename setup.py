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
            'scripts/*'
        ]},
      entry_points={
        'trac.plugins': ['backlog = backlog.web_ui']
        }
      )

