
from re import search
from subprocess import Popen, PIPE

class ServiceBackend:
        
    def get_all_services(self):
        return ['example_1', 'example_2', 'example_3']
    
    def start_service(self, name):
        print "Starting", name
    
    def stop_service(self, name):
        print "Stopping", name
    

class ServiceProxy(ServiceBackend):
    
    def __init__(self):
        self.modules = []
        load = ['sysv']
        
        # check the initd for what we need to load
        p = Popen(['init', '--version'], stdout=PIPE)
        out = p.stdout.read()
        
        match = search('upstart (\d+\.\d+)', out)
        if match:
            if match.group(1) == '0.6':
                load += ['upstart_0_6']
            elif match.group(1) == '0.10':
                load += ['upstart_0_10']
        
        for mod in load:
            self.modules += [__import__('JobService.backends.%s' % mod)]
    
