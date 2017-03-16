#!/usr/bin/env python

PROJECT = 'MTData'

# Change docs/sphinx/conf.py too!
VERSION = '0.2'


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(name=PROJECT,
      version=VERSION,
      description='Data Toolbox for MindTrails Projects',
      long_description=long_description,
      install_requires=['cliff'],
      url='http://github.com/Diheng/MTData',
      author='Diheng Zhang, Dan Funk, Sam Portnow',
      author_email='dzhang@virginia.edu`',
      license='MIT',
      namespace_packages=[],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'MTData = MTData.main:main'
        ],
        'MTData': [
            'export = MTData.export:Export',
            'decode = MTData.recovery:Decode',
            'error = cliffdemo.simple:Error',
            'report = MTData.report:Report',
            'simple = MTData.simple:Simple',
            'list files = cliffdemo.list:Files',
            'files = cliffdemo.list:Files',
            'file = cliffdemo.show:File',
            'show file = cliffdemo.show:File',
            'unicode = cliffdemo.encoding:Encoding',
        ],
    },
      )
