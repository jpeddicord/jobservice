
from dbus import SystemBus, Interface, PROPERTIES_IFACE
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
    
    backend_name = "Upstart 0.6"
        
    def __init__(self):
        """
        Connect to Upstart's dbus service.
        """
        self.jobpaths = {}
        self.instpaths = {}
        self.bus = SystemBus()
        self.upstart = Interface(
            self.bus.get_object('com.ubuntu.Upstart', '/com/ubuntu/Upstart'),
            'com.ubuntu.Upstart0_6'
        )
    
    def get_all_services(self):
        svclist = {}
        for path in self.upstart.GetAllJobs():
            job_obj = self.bus.get_object('com.ubuntu.Upstart', path)
            job_name = job_obj.Get('com.ubuntu.Upstart0_6.Job', 'name',
                                    dbus_interface=PROPERTIES_IFACE)
            job = Interface(job_obj, 'com.ubuntu.Upstart0_6.Job')
            self.jobpaths[job_name] = path
            # get the instance(s) and their states
            instances = job.GetAllInstances()
            self.instpaths[path] = []
            if instances:
                for inst_path in instances:
                    self.instpaths[path].append(inst_path)
                    inst_obj = self.bus.get_object('com.ubuntu.Upstart',
                                                   inst_path)
                    inst_props = inst_obj.GetAll(
                        'com.ubuntu.Upstart0_6.Instance',
                        dbus_interface=PROPERTIES_IFACE
                    )
                    if inst_props['name']:
                        list_name = job_name + '/' + inst_props['name']
                    # if there is no instance name, there's probably only one
                    else:
                        list_name = job_name
                    svclist[list_name] = (inst_props['state'] == 'running')
            # no running instances
            else:
                svclist[job_name] = False
        return svclist
    
    def get_service(self, name):
        # some defaults for values we might not find
        info = {
            'running': False,
            'automatic': False,
            'starton': [],
            'stopon': []
        }
        # get the job name if we're an instance
        if '/' in name:
            job_name = name[:name.index('/')]
            inst_name = name[name.index('/')+1:]
        else:
            job_name = name
            inst_name = None
        # job-level properties
        job_obj = self.bus.get_object('com.ubuntu.Upstart', self.jobpaths[job_name])
        props = job_obj.GetAll('com.ubuntu.Upstart0_6.Job',
                               dbus_interface=PROPERTIES_IFACE)
        # TODO: automatic, starton, stopon
        # running state: check the instance(s)
        for inst_path in self.instpaths[self.jobpaths[job_name]]:
            inst_obj = self.bus.get_object('com.ubuntu.Upstart', inst_path)
            inst_props = inst_obj.GetAll(
                'com.ubuntu.Upstart0_6.Instance',
                dbus_interface=PROPERTIES_IFACE
            )
            # we've found our (named) instance
            if inst_props['name'] == inst_name:
                info['running'] = (inst_props['state'] == 'running')
                break
            # fall back on any available instance
            info['running'] = (inst_props['state'] == 'running')
        return props
    
    def start_service(self, name):
        pass
    
