
from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
        
    def __init__(self):
        """
        Connect to Upstart's dbus service.
        """
        
        self.namepath = {}
        self.bus = SystemBus()
        self.upstart = Interface(
            self.bus.get_object('com.ubuntu.Upstart', '/com/ubuntu/Upstart'),
            'com.ubuntu.Upstart0_6'
        )
    
    def get_all_services(self):
        svclist = []
        for path in self.upstart.GetAllJobs():
            job = self.bus.get_object('com.ubuntu.Upstart', path)
            jobname = job.Get('com.ubuntu.Upstart0_6.Job', 'name',
                              dbus_interface=PROPERTIES_IFACE)
            # cache the name to path mapping
            self.namepath[jobname] = job
            svclist.append(jobname)
        return svclist
        
