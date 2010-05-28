
from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
        
    def __init__(self):
        """
        Connect to Upstart's dbus service.
        """
        self.namepath = {}
        self.instances = {}
        self.bus = SystemBus()
        self.upstart = Interface(
            self.bus.get_object('com.ubuntu.Upstart', '/com/ubuntu/Upstart'),
            'com.ubuntu.Upstart0_6'
        )
    
    def get_all_services(self):
        svclist = []
        for path in self.upstart.GetAllJobs():
            job_obj = self.bus.get_object('com.ubuntu.Upstart', path)
            job_name = job_obj.Get('com.ubuntu.Upstart0_6.Job', 'name',
                                   dbus_interface=PROPERTIES_IFACE)
            job = Interface(job_obj, 'com.ubuntu.Upstart0_6.Job')
            # cache the name to path mapping
            self.namepath[job_name] = job
            # get the instance(s) and their states
            instances = job.GetAllInstances()
            if instances:
                self.instances[path] = []
                for inst_path in instances:
                    inst_obj = self.bus.get_object('com.ubuntu.Upstart',
                                                   inst_path)
                    inst_props = inst_obj.GetAll(
                        'com.ubuntu.Upstart0_6.Instance',
                        dbus_interface=PROPERTIES_IFACE
                    )
                    # cache this instance
                    self.instances[path].append({inst_path: inst_props})
                    if inst_props['name']:
                        list_name = job_name + '/' + inst_props['name']
                    # if there is no instance name, there's probably only one
                    else:
                        list_name = job_name
                    svclist.append((
                        list_name,
                        inst_props['state'] == 'running'
                    ))
            # no running instances
            else:
                svclist.append((job_name, False))
        return svclist
        
