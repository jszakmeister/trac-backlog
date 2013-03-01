from setuptools import setup
import backlog

PACKAGE = 'TracBacklog'

with open('README.rst') as file:
    long_description = file.read()

setup(
    name = PACKAGE,
    version = backlog.get_version(),
    packages = ['backlog'],
    package_data = {
        'backlog': [
            'htdocs/css/*.css',
            'htdocs/img/*.png',
            'htdocs/js/*.js',
            'htdocs/js/dojo/*.js',
            'htdocs/js/dojo/resources/*.gif',
            'htdocs/js/dojo/dnd/*.js',
            'htdocs/js/dojo/date/*.js',
            'htdocs/js/dojo/fx/*.js',
            'htdocs/js/dijit/*.js',
            'htdocs/js/dijit/_base/*.js',
            'htdocs/js/dijit/themes/dijit.css',
            'htdocs/js/dijit/themes/tundra/tundra.css',
            'htdocs/js/dijit/themes/tundra/images/spriteArrows.png',
            'templates/*.html',
      ]},
    entry_points = {
        'trac.plugins': [
            'backlog = backlog.web_ui',
            'backlog_prefs = backlog.prefs',
        ]
    },
    install_requires = [
        'simplejson>=2.0',
    ],
    author = "John Szakmeister",
    author_email = "john@szakmeister.net",
    description = "Enables Trac to be used for managing your ticket backlog.",
    long_description = long_description,
    url = "https://github.com/jszakmeister/trac-backlog",
    license = "BSD",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Trac',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
    ],
)
