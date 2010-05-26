#!/usr/bin/python

from distutils.core import setup

setup_info = dict(
    name='jobservice',
    version='0.1',
    description='jobservice',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobservice',
    packages=['JobService'],
    scripts=['jobservice'],
)

setup(**setup_info)

