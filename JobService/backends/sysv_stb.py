
from dbus import SystemBus, Interface, Array
from dbus.exceptions import DBusException
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
        self._connect()
    
    def _connect(self):
        self.sconfig = Interface(
            self.bus.get_object(
                'org.freedesktop.SystemToolsBackends.ServicesConfig',
                '/org/freedesktop/SystemToolsBackends/ServicesConfig'
            ),
            'org.freedesktop.SystemToolsBackends'
        )
        self.sconfig2 = Interface(
            self.bus.get_object(
                'org.freedesktop.SystemToolsBackends.ServiceConfig2',
                '/org/freedesktop/SystemToolsBackends/ServiceConfig2'
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
        try:
            self.runlevels, self.active_runlevel, services = self.sconfig.get()
        except DBusException:
            self._connect()
            self.runlevels, self.active_runlevel, services = self.sconfig.get()
        for name, runlevels in services:
            self.services[name] = runlevels
            if runlevels:
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
    
    def start_service(self, name):
        self._change_service_state(name, True)
    
    def stop_service(self, name):
        self._change_service_state(name, False)
    
    def _change_service_state(self, name, auto):
        """
        Set a service's stopped state in s-t-b.
        """
        runlevels = []
        for runlevel, stopped, priority in self.services[name]:
            if runlevel == self.active_runlevel:
                stopped = False if auto else True
            runlevels.append((runlevel, stopped, priority))
        service_obj = (name, runlevels)
        try:
            self.sconfig2.set(service_obj)
        except DBusException:
            self._connect()
            self.sconfig2.set(service_obj)
        self.get_all_services() # reload our cache
        
    def _get_lsb_properties(self, name):
        """
        Scan a service's init.d entry for LSB information about it.
        Returns a dictionary of the entries provided.
        """
        props = {}
        try:
            entry = open('/etc/init.d/{0}'.format(name), 'r')
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
