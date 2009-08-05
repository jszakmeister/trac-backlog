from setuptools import setup

PACKAGE = 'TracBacklog'
VERSION = '0.1'

setup(name=PACKAGE,
      version=VERSION,
      packages=['backlog'],
      entry_points='''
          [trac.plugins]
          backlog = backlog.web_ui
      ''')

