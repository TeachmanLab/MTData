try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='MTData',
      version='0.1',
      description='Data Toolbox for MindTrails Projects',
      url='http://github.com/Diheng/MTData',
      author='Diheng Zhang, Dan Funk, Sam Portnow',
      author_email='dzhang@virginia.edu`',
      license='MIT',
      packages=['MTData'],
      zip_safe=False)
