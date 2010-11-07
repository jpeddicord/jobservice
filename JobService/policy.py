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

import logging
from dbus import SystemBus, DBusException, Interface

log = logging.getLogger('policy')

class DeniedByPolicy(DBusException):
    _dbus_error_name = 'com.ubuntu.JobService.DeniedByPolicy'

class Policy:
    
    def __init__(self, enforce=True):
        self.enforce = enforce
        self.bus = SystemBus()
        self.dbus_iface = None
        self.pk = Interface(self.bus.get_object('org.freedesktop.PolicyKit1',
                '/org/freedesktop/PolicyKit1/Authority'),
                'org.freedesktop.PolicyKit1.Authority')
        
        if not enforce:
            log.warn('Not enforcing PolicyKit privileges!')
    
    def check(self, sender, conn, priv='com.ubuntu.jobservice.manage'):
        """
        Check or ask for authentication for job management.
        """
        if not self.enforce: return
        log.debug('Asking for PolicyKit authorization')
        # get the PID of the sender
        if not self.dbus_iface:
            self.dbus_iface = Interface(conn.get_object('org.freedesktop.DBus',
                    '/org/freedesktop/DBus/Bus'), 'org.freedesktop.DBus')
        pid = self.dbus_iface.GetConnectionUnixProcessID(sender)
        # ask PolicyKit
        auth, challenge, details = self.pk.CheckAuthorization(
                ('unix-process', {'pid': pid, 'start-time': 0}),
                priv, {'': ''}, 1, '', timeout=500)
        if not auth:
            log.info('Authorization failed')
            raise DeniedByPolicy('Not authorized to manage jobs.')
        log.debug('Authorization passed')
        
            
