# This file is part of jobservice.
# Copyright 2010 Jacob Peddicord <jpeddicord@ubuntu.com>
#
# jobservice is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jobservice is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with jobservice.  If not, see <http://www.gnu.org/licenses/>.

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
            self.jobs.append(SingleJobService(conn,
                '/'.join((DBUS_PATH, dbus_safe_name(job))),
                name=job, root=self
            ))
        
        log.info('Ready')
        
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
