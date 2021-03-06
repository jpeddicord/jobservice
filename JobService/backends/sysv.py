# This file is part of jobservice.
# Copyright 2010 Jacob Peddicord <jpeddicord@ubuntu.com>
#
# jobservice is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jobservice is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jobservice.  If not, see <http://www.gnu.org/licenses/>.

import os
from stat import ST_MODE, S_ISLNK, S_IXUSR
from subprocess import Popen, PIPE, check_call, CalledProcessError
from dbus import Array
from JobService import DBUS_IFACE, JobException
from JobService.backends import ServiceBase


class SysVException(JobException):
    _dbus_error_name = DBUS_IFACE + '.SysVException'

class ServiceBackend(ServiceBase):
        
    def __init__(self):
        self.runlevels = self._get_runlevel_info()
        self.current = self._get_current_runlevel()
    
    def get_all_services(self):
        svclist = []
        for root, dirs, files in os.walk('/etc/init.d/'):
            for svc in files:
                path = os.path.join(root, svc)
                mode = os.lstat(path).st_mode
                # we only want regular, executable files
                if not S_ISLNK(mode) and bool(mode & S_IXUSR):
                    # ignore files not linked in rc.d
                    if svc in self.runlevels:
                        svclist.append(svc)
            break
        return svclist
    
    def get_service(self, name):
        info = {
            'name': name,
            'description': '',
            'version': '',
            'author': '',
            'running': False,
            'automatic': False,
            'pid': 0,
            'starton': Array(signature='s'),
            'stopon': Array(signature='s'),
            'file': '',
        }
        # check the file for info
        props = self._get_lsb_properties(name)
        info['file'] = props['file']
        if 'Short-Description' in props:
            info['description'] = props['Short-Description']
        # look through runlevel information
        if name in self.runlevels:
            for rlvl, start in self.runlevels[name].iteritems():
                if start[0] == True:
                    info['starton'].append(rlvl)
                else:
                    info['stopon'].append(rlvl)
                if rlvl == self.current:
                    info['automatic'] = start[0]
        p = Popen(['/etc/init.d/' + name, 'status'], stdout=PIPE, stderr=PIPE)
        p.communicate()   # eat stdout/stdin
        info['running'] = (p.returncode == 0)
        return info
    
    def start_service(self, name):
        try:
            check_call(['/etc/init.d/' + name, 'start'])
        except CalledProcessError, e:
            raise SysVException('Start failed: code {0}'.format(e.returncode))
        try:
            check_call(['/etc/init.d/' + name, 'status'], stdout=PIPE, stderr=PIPE)
        except CalledProcessError, e:
            raise SysVException('Service stopped running unexpectedly.')
    
    def stop_service(self, name):
        try:
            check_call(['/etc/init.d/' + name, 'stop'])
        except CalledProcessError, e:
            raise SysVException('Stop failed: code {0}'.format(e.returncode))
    
    def set_service_automatic(self, name, auto):
        if self.current not in self.runlevels[name]:
            raise SysVException('Unsupported runlevel.')
        self._remove_rc(name, self.current)
        self._link_rc(name, self.current, auto)
        self.runlevels[name][self.current] = (auto,
                self.runlevels[name][self.current][1])
    
    def _get_runlevel_info(self):
        """Parse /etc/rc?.d and store symlink information.
        
        Returns a dictionary with service names as keys, and a dict of
        runlevel: (bool start, int priority) pairs with found information.
        """
        svcs = {}
        for runlevel in ('0', '1', '2', '3', '4', '5', '6', '7', 'S'):
            for root, dirs, files in os.walk('/etc/rc{0}.d'.format(runlevel)):
                for svc in files:
                    path = os.path.join(root, svc)
                    # exec only
                    if not bool(os.lstat(path).st_mode & S_IXUSR):
                        continue
                    start = (svc[:1] == 'S')
                    pri = int(svc[1:3])
                    name = svc[3:]
                    if not name in svcs:
                        svcs[name] = {}
                    svcs[name][runlevel] = (start, pri)
                break
        return svcs
    
    def _remove_rc(self, name, rlvl):
        """Unlink a service from an rc#.d directory"""
        pri = str(self.runlevels[name][rlvl][1])
        mode = 'S' if self.runlevels[name][rlvl][0] else 'K'
        os.unlink('/etc/rc{0}.d/{1}{2}{3}'.format(rlvl, mode, pri, name))
    
    def _link_rc(self, name, rlvl, start):
        """Re-link an init script to the proper rc#.d location"""
        pri = str(self.runlevels[name][rlvl][1])
        mode = 'S' if start else 'K'
        os.symlink('/etc/init.d/' + name,
                   '/etc/rc{0}.d/{1}{2}{3}'.format(rlvl, mode, pri, name))
    
    def _get_current_runlevel(self):
        out = Popen(['/sbin/runlevel'], stdout=PIPE).communicate()[0]
        return out.split()[1]
    
    def _get_lsb_properties(self, name):
        """
        Scan a service's init.d entry for LSB information about it.
        Returns a dictionary of the entries provided.
        """
        props = {'file': '/etc/init.d/' + name}
        try:
            entry = open(props['file'])
        except IOError: return props
        parsing = False
        for line in entry:
            if not parsing:
                if '### BEGIN INIT INFO' in line:
                    parsing = True
                continue
            if '### END INIT INFO' in line:
                break
            try:
                key, value = line[2:].split(': ')
            except: continue
            props[key] = value.strip()
        entry.close()
        return props
