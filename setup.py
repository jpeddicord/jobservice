#!/usr/bin/python

from os import listdir
from os.path import exists
from subprocess import Popen, PIPE
from distutils.core import setup
from distutils.command.install import install
from distutils.core import Command

class install_fix_paths(Command):
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        prefix = self.get_finalized_command('install').prefix
        data_dir = self.get_finalized_command('install_data').install_dir
        lib_dir = self.get_finalized_command('install_lib').install_dir
        # dbus service
        for iface in ('com.ubuntu.JobService', 'com.ubuntu.JobService.Job'):
            fn = data_dir + '/share/dbus-1/system-services/' + iface + '.service'
            with open(fn) as f:
                data = f.read()
            with open(fn, 'w') as f:
                f.write(data.replace('Exec=/usr', 'Exec=' + prefix))
        # info.py
        fn = lib_dir + '/JobService/info.py'
        with open(fn) as f:
            data = f.read()
        with open(fn, 'w') as f:
            f.write(data.replace("prefix = '/usr'", "prefix = '{0}'".format(prefix)))

setup_info = dict(
    name='jobservice',
    version='0.8.1',
    description='jobservice',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobservice',
    cmdclass={'install_fix_paths': install_fix_paths},
    packages=['JobService', 'JobService.backends'],
    data_files=[
        ('/etc/dbus-1/system.d/', ['com.ubuntu.JobService.conf']),
        ('share/dbus-1/system-services/', ['com.ubuntu.JobService.service', 'com.ubuntu.JobService.Job.service']),
        ('share/polkit-1/actions/', ['com.ubuntu.jobservice.policy']),
        ('share/jobservice/default/', ['sls/'+x for x in listdir('sls')]),
        ('lib/jobservice/helpers/', ['helpers/'+x for x in listdir('helpers')]),
        ('sbin/', ['jobservice']),
    ],
)

# get the bzr revision if applicable
if 'bzr' in setup_info['version']:
    try:
        setup_info['version'] += Popen(['bzr', 'revno'],stdout=PIPE).communicate()[0].strip()
    except: pass

# write out info
with open('JobService/info.py', 'w') as f:
    for item in ('name', 'version', 'author', 'author_email', 'url'):
        f.write("%s = '%s'\n" % (item, setup_info[item]))
    f.write("prefix = '/usr'\n") # overwritten by fix_paths

# update translations if available (needed for branch builds)
if exists('./translations.sh'):
    Popen(['./translations.sh']).communicate()

# generate documentation
try:
    from docutils.core import publish_file
    from docutils.writers import manpage, html4css1
    publish_file(source_path='doc/manpage.txt', destination_path='jobservice.1', writer=manpage.Writer())
    publish_file(source_path='doc/sls-format-0.8.txt', destination_path='doc/sls-format-0.8.html', writer=html4css1.Writer(), settings_overrides={'stylesheet_path': 'doc/style.css'})
except: pass

install.sub_commands.append(('install_fix_paths', None))
setup(**setup_info)

