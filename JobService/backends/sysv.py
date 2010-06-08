
from dbus import SystemBus, Interface, Array
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
        
    def __init__(self):
        """
        Connect to system-tools-backends.
        """
        self.runlevels = []
        self.active_runlevel = -1
        self.services = {}
        
        self.bus = SystemBus()
        self.stb = Interface(
            self.bus.get_object(
                'org.freedesktop.SystemToolsBackends.ServicesConfig',
                '/org/freedesktop/SystemToolsBackends/ServicesConfig'
            ),
            'org.freedesktop.SystemToolsBackends'
        )
    
    def get_all_services(self):
        """
        Return our list of services and states.
        We guess at a service's state by seeing if it _should_ be running,
        but if it crashed or was stopped then we don't know.
        """
        svclist = []
        self.runlevels, self.active_runlevel, services = self.stb.get()
        for name, runlevels in services:
            self.services[name] = runlevels
            svclist.append(name)
        return svclist
    
    def get_service(self, name):
        info = {
            'name': name,
            'description': '',
            'version': '',
            'author': '',
            'running': False,
            'automatic': False,
            'starton': Array(signature='s'),
            'stopon': Array(signature='s'),
        }
        props = self._get_lsb_properties(name)
        if 'Short-Description' in props:
            info['description'] = props['Short-Description']
        # get the runlevels & implied running state
        for runlevel, stopped, priority in self.services[name]:
            if runlevel == self.active_runlevel:
                info['automatic'] = (stopped == 0)
                info['running'] = info['automatic']
            if stopped:
                info['stopon'].append(runlevel)
            else:
                info['starton'].append(runlevel)
        return info
        
    def _get_lsb_properties(self, name):
        """
        Scan a service's init.d entry for LSB information about it.
        Returns a dictionary of the entries provided.
        """
        props = {}
        try:
            entry = open('/etc/init.d/%s' % name, 'r')
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
