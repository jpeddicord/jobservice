
import logging
from re import search
from subprocess import Popen, PIPE
from dbus import Array
from JobService.settings import ServiceSettings

log = logging.getLogger('backends')

BACKENDS = []   # automatic if empty

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
    
    def get_service_settings(self, name):
        return {}
    
    def set_service_settings(self, name, newsettings):
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
                self.bksls[svc] = bk.get_service_settings(svc)
            svclist += services
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
    
    def get_service_settings(self, name, lang=''):
        # settings added by backend
        settings = self.bkmap[name].get_service_settings(name)
        if name in self.sls:
            # xml settings
            for sname in self.sls[name].get_all_settings():
                settings[sname] = self.sls[name].get_setting(sname, lang)
        return settings
    
    def set_service_settings(self, name, newsettings):
        extra = {}
        for sname, svalue in newsettings.iteritems():
            try:
                self.sls[name].set_setting(sname, svalue)
            # if it's in the XML, it's probably from the backend
            except KeyError:
                extra[sname] = svalue
        # send the leftover settings to the backend
        self.bkmap[name].set_service_settings(name, extra)


def _auto_backends():
    """Return a list of available backends on this system."""
    
    # start with sysv
    load = ['sysv']
        
    # check for upstart
    p = Popen(['/sbin/init', '--version'], stdout=PIPE)
    out = p.stdout.read()
    match = search('upstart (\d+\.\d+)', out)
    if match:
        if match.group(1) == '0.6':
            load += ['upstart_0_6']
        elif match.group(1) == '0.10':
            load += ['upstart_0_10']
    return load
