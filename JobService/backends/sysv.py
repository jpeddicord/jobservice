
import os
from stat import ST_MODE, S_ISLNK, S_IXUSR
from subprocess import Popen, PIPE, check_call, CalledProcessError
from dbus import Array
from JobService import DBUS_IFACE, JobException
from JobService.backends import ServiceBase


class SysVException(JobException):
    _dbus_error_name = DBUS_IFACE + '.SysVException'

class ServiceBackend(ServiceBase):
        
    def __init__(self):
        self.runlevels = self._get_runlevel_info()
        self.current = self._get_current_runlevel()
        self.running = {}
    
    def get_all_services(self):
        svclist = []
        for root, dirs, files in os.walk('/etc/init.d/'):
            for svc in files:
                path = os.path.join(root, svc)
                mode = os.lstat(path).st_mode
                # we only want regular, executable files
                if not S_ISLNK(mode) and bool(mode & S_IXUSR):
                    # ignore files not linked in rc.d
                    if svc in self.runlevels:
                        svclist.append(svc)
            break
        return svclist
    
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
        # check the file for info
        props = self._get_lsb_properties(name)
        info['file'] = props['file']
        if 'Short-Description' in props:
            info['description'] = props['Short-Description']
        # look through runlevel information
        if name in self.runlevels:
            for rlvl, start in self.runlevels[name].iteritems():
                if start[0] == True:
                    info['starton'].append(str(rlvl))
                else:
                    info['stopon'].append(str(rlvl))
                if rlvl == self.current:
                    info['automatic'] = start[0]
        # we cannot reliably determine this, so we fudge by storing.
        if name in self.running:
            info['running'] = self.running[name]
        else:
            info['running'] = info['automatic']
        return info
    
    def start_service(self, name):
        try:
            check_call(['/etc/init.d/' + name, 'start'])
        except CalledProcessError, e:
            raise SysVException('Start failed: code {0}'.format(e.returncode))
        self.running[name] = True
    
    def stop_service(self, name):
        try:
            check_call(['/etc/init.d/' + name, 'stop'])
        except CalledProcessError, e:
            raise SysVException('Stop failed: code {0}'.format(e.returncode))
        self.running[name] = False
    
    def set_service_automatic(self, name, auto):
        pass #TODO
    
    def get_service_settings(self, name, lang):
        settings = []
        if not name in self.runlevels:
            return settings
        for rlvl, start in self.runlevels[name].iteritems():
            settings.append(('runlevel_{0}'.format(rlvl), 'bool',
                "Active on runlevel {runlevel}".format(runlevel=rlvl), #XXX: i18n
                'true' if start[0] else 'false',
                (('true', ''), ('false', '')), {}
            ))
        return settings
    
    def _get_runlevel_info(self):
        """Parse /etc/rc?.d and store symlink information.
        
        Returns a dictionary with service names as keys, and a dict of
        runlevel: (bool start, int priority) pairs with found information.
        """
        svcs = {}
        for runlevel in range(0, 7):
            for root, dirs, files in os.walk('/etc/rc{0}.d'.format(runlevel)):
                for svc in files:
                    path = os.path.join(root, svc)
                    # exec only
                    if not bool(os.lstat(path).st_mode & S_IXUSR):
                        continue
                    start = (svc[:1] == 'S')
                    pri = int(svc[1:3])
                    name = svc[3:]
                    if not name in svcs:
                        svcs[name] = {}
                    svcs[name][runlevel] = (start, pri)
                break
        return svcs
      
    def _update_rcd(self):
        """Run update-rd.d"""
        pass
    
    def _get_current_runlevel(self):
        out = Popen(['/sbin/runlevel'], stdout=PIPE).communicate()[0]
        return int(out.split()[1])
    
    def _get_lsb_properties(self, name):
        """
        Scan a service's init.d entry for LSB information about it.
        Returns a dictionary of the entries provided.
        """
        props = {'file': '/etc/init.d/' + name}
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
