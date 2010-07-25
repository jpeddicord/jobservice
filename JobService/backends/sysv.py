
import os
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
        
    def __init__(self):
        self.runlevels = []
        self.active_runlevel = -1
        self.services = {}
    
    def get_all_services(self):
        for root, dirs, files in os.walk('/etc/init.d/'):
            for fi in files:
                pass
        return []
    
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
        return info
    
    def start_service(self, name):
        pass
    
    def stop_service(self, name):
        pass
        
    def _get_lsb_properties(self, name):
        """
        Scan a service's init.d entry for LSB information about it.
        Returns a dictionary of the entries provided.
        """
        props = {'file': '/etc/init.d/{0}'.format(name)}
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
