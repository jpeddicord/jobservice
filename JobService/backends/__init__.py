
from re import search
from subprocess import Popen, PIPE


class ServiceBase:
        
    def get_all_services(self):
        return []
    
    def get_service(self, name):
        return {
            'name': 'example-service',
            'description': 'an example service',
            'version': '0.1',
            'author': 'Nobody',
            'running': False,
            'automatic': False,
            'dependencies': ['example-base'],
            'runlevels': [2, 3],
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
        self.backends = []
        self.svcmap = {}
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
            self.backends += [newbackend]
            self.svcmap[newbackend] = []
    
    def get_all_services(self):
        svclist = {}
        for bk in self.backends:
            svclist.update(bk.get_all_services())
        return svclist
    
