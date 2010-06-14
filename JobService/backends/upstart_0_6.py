
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
        # starton/stopon
        conf = open('/etc/init/{0}.conf'.format(job_name), 'r')
        starton = self._parse_conf(conf, 'start on')
        stopon = self._parse_conf(conf, 'stop on')
        info['starton'] += self._extract_events(starton)
        info['stopon'] += self._extract_events(stopon)
        # automatic if starton isn't commented out
        info['automatic'] = (starton[0] != '#')
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
    
    def _parse_conf(self, conf, find):
        """
        Parse file 'conf' for text 'find' and return the value.
        Useful for grabbing the full contents of a start/stop on line.
        """
        conf.seek(0)
        reading = False
        data = ""
        paren = 0
        for line in conf:
            # could be at pos 1 or 2 if line is commented out
            pos = line.find(find)
            if pos >= 0 and pos <= 2:
                reading = True
            if reading:
                data += line
                paren += line.count('(') - line.count(')')
                if not paren:
                    break
        return data
    
    def _extract_events(self, data):
        """
        Grab events present in a text string (ie, a start/stop on line).
        An event could be a runlevel or a starting/stopping string.
        """
        events = []
        keywords = ('starting', 'stopping', 'started', 'stopped', 'runlevel')
        words = [d.strip(' ()') for d in data.split()]
        i = 0
        for w in words:
            if w in keywords:
                if w == 'runlevel':
                    levels = words[i+1].strip('[]')
                    if levels[0] == '!':
                        events.append('not runlevels {0}'.format(' '.join(levels[1:])))
                    else:
                        events.append('runlevels {0}'.format(' '.join(levels)))
                else:
                    events.append('{0} {1}'.format(w, words[i+1]))
            i += 1
        return events
