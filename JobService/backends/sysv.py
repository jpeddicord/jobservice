
from dbus import SystemBus, Interface
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
        
    backend_name = "System V"
        
    def __init__(self):
        """
        Connect to system-tools-backends.
        """
        self.runlevels = []
        
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
        svclist = {}
        self.runlevels, self.active_runlevel, services = self.stb.get()
        for name, runlevels in services:
            running = False
            # find our runlevel
            for level, stopped, priority in runlevels:
                if level == self.active_runlevel:
                    running = False if stopped else True
                    break
            svclist[name] = running
        return svclist
    
