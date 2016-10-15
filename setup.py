#!/usr/bin/env python

from distutils.core import setup

long_description='''
This program addresses the irritating problem of applying
regular expressions and other common simple text processing
methods to balanced tags within an XML document.  It gives
you enough rope to hang yourself with; it is _not_ a fully
fledged XML tool.
'''.strip()

setup(name='nugsl-tagtool',
      version='1.5',
      description='Apply a function to balanced XML tag environments',
      author='Frank Bennett',
      author_email='biercenator@gmail.com',
      maintainer='Frank Bennett',
      maintainer_email='biercenator@gmail.com',
      url='http://gsl-nagoya-u.net/',
      packages=['nugsl','nugsl.tagtool'],
      provides=['nugsl.tagtool'],
      package_dir={'nugsl':''},
      long_description=long_description,
      platforms=['any'],
      license='http://www.gnu.org/copyleft/gpl.html'
      )
