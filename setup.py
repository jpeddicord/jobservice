#!/usr/bin/python

from distutils.core import setup

setup_info = dict(
    name='jobservice',
    version='0.1',
    description='jobservice',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobservice',
    packages=['JobService', 'JobService.backends'],
    scripts=['jobservice'],
    data_files=[
        ('share/dbus-1/system-services/', ['com.ubuntu.JobService.service']),
        ('/etc/dbus-1/system.d/', ['com.ubuntu.JobService.conf'])
        ('share/polkit-1/actions', ['com.ubuntu.jobservice.policy']),
    ],
)

#TODO: modify com.ubuntu.JobService.service to replace the installation path

setup(**setup_info)

