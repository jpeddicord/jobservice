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

import logging
from re import search
from subprocess import Popen, PIPE
from dbus import Array
from JobService.settings import ServiceSettings

log = logging.getLogger('backends')

BACKENDS = []   # automatic if empty
                # distributors can manually set this for efficiency

class ServiceBase:
    
    def get_all_services(self):
        return []
    
    def get_service(self, name):
        return {
            'name': 'undefined',
            'description': 'service unknown',
            'version': '0',
            'author': 'Nobody',
            'running': False,
            'automatic': False,
            'pid': 0,
            'starton': Array(signature='s'),
            'stopon': Array(signature='s'),
            'file': '',
        }
    
    def start_service(self, name):
        pass
    
    def stop_service(self, name):
        pass
    
    def set_service_automatic(self, name, auto):
        pass
    
    def get_service_settings(self, name, lang):
        return []
    
    def set_service_settings(self, name, newsettings):
        pass

    def validate_service_setting(self, name, setting, value):
        pass

class ServiceProxy(ServiceBase):
    """
    Fake backend object that calls upon one or more real service backends
    to do the heavy lifting.
    """
    
    def __init__(self):
        """
        Load the appropriate backends for the current system.
        """
        self.backends = []
        self.bkmap = {}
        self.sls = {}
        self.bksls = {}
        
        if BACKENDS:
            load = BACKENDS
            log.debug('Backends set to: ' + ', '.join(load))
        else:
            load = _auto_backends()
            log.debug('Autoloading backends: ' + ', '.join(load))
        
        # load the backends
        for mod in load:
            newmod = __import__('JobService.backends.' + mod,
                    fromlist=['ServiceBackend'])
            self.backends.append(newmod.ServiceBackend())
        
    def get_all_services(self):
        svclist = []
        # get the services
        for bk in self.backends:
            services = bk.get_all_services()
            for svc in services:
                self.bkmap[svc] = bk
                # check for SLS
                try:
                    self.sls[svc] = ServiceSettings(svc)
                except: pass
                # and query the backend for additional settings
                self.bksls[svc] = bk.get_service_settings(svc, '')
                # no duplicates (backends will still properly override)
                if not svc in svclist:
                    svclist.append(svc)
        return svclist
    
    def get_service(self, name):
        bk = self.bkmap[name]
        info = {'backend': bk.__module__[bk.__module__.rfind('.')+1:],
                'settings': name in self.sls or len(self.bksls[name])}
        info.update(bk.get_service(name))
        return info
    
    def start_service(self, name):
        self.bkmap[name].start_service(name)
        log.info("Started {0}".format(name))
    
    def stop_service(self, name):
        self.bkmap[name].stop_service(name)
        log.info("Stopped {0}".format(name))
    
    def set_service_automatic(self, name, auto):
        self.bkmap[name].set_service_automatic(name, auto)
        log.info("Set {0} to {1}".format(name, 'auto' if auto else 'manual'))
    
    def get_service_settings(self, name, lang=''):
        settings = []
        snames = []
        # xml settings
        if name in self.sls:
            for s in self.sls[name].get_all_settings():
                settings.append(self.sls[name].get_setting(s, lang))
                snames.append(s)
        # settings added by backend
        for s in self.bkmap[name].get_service_settings(name, lang):
            if not s[0] in snames:
                settings.append(s)
        return settings
    
    def set_service_settings(self, name, newsettings):
        # validate *all* settings before applying *any*
        for s in newsettings:
            self.validate_service_setting(name, s, newsettings[s])
        # if no exception occurred, we're good
        if name in self.sls:
            for s in self.sls[name].get_all_settings():
                if s in newsettings:
                    self.sls[name].set_setting(s, newsettings.pop(s))
        # send the leftover settings to the backend
        self.bkmap[name].set_service_settings(name, newsettings)

    def validate_service_setting(self, name, setting, value):
        # verify by provided SLS if available
        if name in self.sls and setting in self.sls[name].get_all_settings():
            return self.sls[name].validate_setting(setting, value)
        # otherwise let the backend verify
        else:
            return self.bkmap[name].validate_service_setting(name, setting, value)
    

def _auto_backends():
    """Return a list of available backends on this system."""
    
    # start with sysv
    load = ['sysv']
        
    # check for upstart 0.6|0.10
    p = Popen(['/sbin/init', '--version'], stdout=PIPE)
    out = p.stdout.read()
    match = search('upstart (\d+\.\d+)', out)
    if match:
        if match.group(1) == '0.6' or match.group(1) == '0.8':
            load += ['upstart_0_6']
        else:
            load += ['upstart_1']
    return load
