
import sys
import logging
from dbus.service import Object as DBusObject, method as DBusMethod
from JobService import DBUS_PATH, DBUS_IFACE
from JobService.backends import ServiceProxy
from JobService.job import SingleJobService
from JobService.policy import Policy
from JobService.util import dbus_safe_name

log = logging.getLogger('jobservice')

class RootJobService(DBusObject):

    def __init__(self, conn=None, object_path=None, bus_name=None, idle=None, enforce=True):
        """
        Fire up this service as well as all of the paths for individual jobs.
        """
        DBusObject.__init__(self, conn, object_path, bus_name)
        
        self.idle = idle
        self.policy = Policy(enforce)
        self.proxy = ServiceProxy()
        self.jobs = []
        
        allsvcs = self.proxy.get_all_services()
        for job in allsvcs:
            self.jobs.append(SingleJobService(
                conn,
                '%s/%s' % (DBUS_PATH, dbus_safe_name(job)),
                name=job,
                root=self
            ))
        
    @DBusMethod(DBUS_IFACE, in_signature='', out_signature='a(so)',
                sender_keyword='sender', connection_keyword='conn')
    def GetAllJobs(self, sender=None, conn=None):
        """
        Returns all jobs known by the backend(s), along with their states.
        
        Returns array of struct (
            string name
            object path
        )
        """
        self.idle.ping()
        log.debug("GetAllJobs called")
        svclist = []
        for job in self.jobs:
            svclist.append((job.name, job.path))
        return svclist
