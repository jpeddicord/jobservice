#!/usr/bin/python

from os import listdir
from distutils.core import setup
from subprocess import Popen, PIPE


setup_info = dict(
    name='jobservice',
    version='0.1~bzr',
    description='jobservice',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobservice',
    packages=['JobService', 'JobService.backends'],
    scripts=['jobservice'],
    data_files=[
        ('share/dbus-1/system-services/', ['com.ubuntu.JobService.service']),
        ('/etc/dbus-1/system.d/', ['com.ubuntu.JobService.conf']),
        ('share/polkit-1/actions/', ['com.ubuntu.jobservice.policy']),
        ('share/jobservice/sls/', ['sls/{0}'.format(x) for x in listdir('sls')]),
    ],
)

# get the bzr revision if applicable
if 'bzr' in setup_info['version']:
    try:
        setup_info['version'] += Popen(['bzr', 'revno'],stdout=PIPE).communicate()[0].strip()
    except: pass

#TODO: modify com.ubuntu.JobService.service to replace the installation path
#TODO: build_i18n

setup(**setup_info)

