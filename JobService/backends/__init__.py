
import logging
from re import search
from subprocess import Popen, PIPE
from dbus import Array
from JobService.settings import ServiceSettings

log = logging.getLogger('jobservice.backends')

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
        print "Starting", name
    
    def stop_service(self, name):
        print "Stopping", name
    

class ServiceProxy(ServiceBase):
    """
    Fake backend object that calls upon one or more real service backends
    to do the heavy lifting.
    """
    
    def __init__(self):
        """
        Load the appropriate backends for the current system.
        """
        self.backends = {}
        self.sls = {}
        load = ['sysv_stb']
        
        # check for upstart
        p = Popen(['/sbin/init', '--version'], stdout=PIPE)
        out = p.stdout.read()
        
        match = search('upstart (\d+\.\d+)', out)
        if match:
            if match.group(1) == '0.6':
                load += ['upstart_0_6']
            elif match.group(1) == '0.10':
                load += ['upstart_0_10']
        
        # load the backends
        for mod in load:
            newmod = __import__('JobService.backends.' + mod,
                    fromlist=['ServiceBackend'])
            newbackend = newmod.ServiceBackend()
            self.backends[newbackend] = []
        
    def get_all_services(self):
        svclist = []
        # get the services
        for bk in self.backends:
            self.backends[bk] = bk.get_all_services()
            svclist += self.backends[bk]
        # initalize setting backends
        for svc in svclist:
            try:
                self.sls[svc] = ServiceSettings(svc)
            except: pass
        return svclist
    
    def get_service(self, name):
        for bk in self.backends:
            if name in self.backends[bk]:
                info = {'backend': bk.__module__[bk.__module__.rfind('.')+1:],
                        'settings': name in self.sls}
                info.update(bk.get_service(name))
                return info
    
    def start_service(self, name):
        for bk in self.backends:
            if name in self.backends[bk]:
                bk.start_service(name)
                log.info("Started {0}".format(name))
    
    def stop_service(self, name):
        for bk in self.backends:
            if name in self.backends[bk]:
                bk.stop_service(name)
                log.info("Stopped {0}".format(name))
    
    def get_service_settings(self, name):
        settings = {}
        if name in self.sls:
            for sname in self.sls[name].get_all_settings():
                settings[sname] = self.sls[name].get_setting(sname)
        return settings
        #TODO: query the backends for additional settings
    
    def set_service_settings(self, name, newsettings):
        if name in self.sls:
            for sname in newsettings:
                self.sls[name].set_setting(sname, newsettings[sname])
        #TODO: send the remaining settings to backends
    
