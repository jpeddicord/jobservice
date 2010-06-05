
from re import search
from subprocess import Popen, PIPE


class ServiceBase:
    
    backend_name = "Undefined"
        
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
            'starton': [''],
            'stopon': [''],
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
        load = ['sysv']
        
        # check for upstart
        p = Popen(['init', '--version'], stdout=PIPE)
        out = p.stdout.read()
        
        match = search('upstart (\d+\.\d+)', out)
        if match:
            if match.group(1) == '0.6':
                load += ['upstart_0_6']
            elif match.group(1) == '0.10':
                load += ['upstart_0_10']
        
        # load the backends
        for mod in load:
            newmod = __import__('JobService.backends.%s' % mod,
                                fromlist=['ServiceBackend'])
            newbackend = newmod.ServiceBackend()
            self.backends[newbackend] = []
        
    def get_all_services(self):
        """
        Get all services from all backends.
        """
        svclist = {}
        for bk in self.backends:
            self.backends[bk] = bk.get_all_services()
            svclist.update(self.backends[bk])
        return svclist
    
    def get_service(self, name):
        """
        Get a single service from the appropriate backend.
        """
        for bk in self.backends:
            # check backend lists for services
            if name in self.backends[bk]:
                info = {'backend': bk.backend_name}
                info.update(bk.get_service(name))
                return info
    
    def start_service(self, name):
        for bk in self.backends:
            if name in self.backends[bk]:
                bk.start_service(name)
    
    def stop_service(self, name):
        for bk in self.backends:
            if name in self.backends[bk]:
                bk.stop_service(name)
                    
