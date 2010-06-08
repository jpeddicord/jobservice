
from dbus import SystemBus, Interface, PROPERTIES_IFACE, Array
from JobService.backends import ServiceBase


class ServiceBackend(ServiceBase):
    
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
        svclist = []
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
                    inst_name = inst_obj.Get('com.ubuntu.Upstart0_6.Instance',
                            'name', dbus_interface=PROPERTIES_IFACE)
                    if inst_name:
                        svclist.append(job_name + '/' + inst_name)
                    # if there is no instance name, there's probably only one
                    else:
                        svclist.append(job_name)
            # no running instances
            else:
                svclist.append(job_name)
        return svclist
    
    def get_service(self, name):
        # some defaults for values we might not find
        info = {
            'running': False,
            'automatic': False,
            'starton': Array(signature='s'),
            'stopon': Array(signature='s'),
        }
        # get the job name if we're an instance
        if '/' in name:
            job_name, inst_name = name.split('/')
        else:
            job_name = name
            inst_name = None
        # job-level properties
        job_obj = self.bus.get_object('com.ubuntu.Upstart',
                self.jobpaths[job_name])
        props = job_obj.GetAll('com.ubuntu.Upstart0_6.Job',
                dbus_interface=PROPERTIES_IFACE)
        # TODO: automatic, starton, stopon
        # running state: check the instance(s)
        for inst_path in self.instpaths[self.jobpaths[job_name]]:
            inst_obj = self.bus.get_object('com.ubuntu.Upstart', inst_path)
            inst_props = inst_obj.GetAll('com.ubuntu.Upstart0_6.Instance',
                    dbus_interface=PROPERTIES_IFACE)
            info['running'] = (inst_props['state'] == 'running')
            # we've found our (named) instance
            if inst_props['name'] == inst_name:
                info['running'] = (inst_props['state'] == 'running')
                break
        info.update(props)
        return info
    
    def start_service(self, name):
        """
        If a job is given, try to start it's instance first if it has one.
        If it doesn't have one, start via job.
        If an instance is given, start it directly.
        """
        if '/' in name:
            job_name, inst_name = name.split('/')
        else:
            job_name = name
            inst_name = None
        # no instances, start the job
        if not self.instpaths[self.jobpaths[job_name]]:
            job_obj = self.bus.get_object('com.ubuntu.Upstart',
                    self.jobpaths[job_name])
            job = Interface(job_obj, 'com.ubuntu.Upstart0_6.Job')
            job.Start([], True)
        # one or more instances available
        else:
            for inst_path in self.instpaths[self.jobpaths[job_name]]:
                inst_obj = self.bus.get_object('com.ubuntu.Upstart', inst_path)
                inst_props = inst_obj.GetAll('com.ubuntu.Upstart0_6.Instance',
                        dbus_interface=PROPERTIES_IFACE)
                # stop on the named instance
                if inst_props['name'] == inst_name:
                    break
            inst_obj.Start(True, dbus_interface='com.ubuntu.Upstart0_6.Instance')
        # reload
        self.get_all_services()
        
    def stop_service(self, name):
        """
        Find the appropritate job instance (named, if available) and stop it.
        """
        if '/' in name:
            job_name, inst_name = name.split('/')
        else:
            job_name = name
            inst_name = None
        for inst_path in self.instpaths[self.jobpaths[job_name]]:
            inst_obj = self.bus.get_object('com.ubuntu.Upstart', inst_path)
            inst_props = inst_obj.GetAll('com.ubuntu.Upstart0_6.Instance',
                    dbus_interface=PROPERTIES_IFACE)
            if inst_props['name'] == inst_name:
                break
        inst_obj.Stop(True, dbus_interface='com.ubuntu.Upstart0_6.Instance')
        # reload
        self.get_all_services()
