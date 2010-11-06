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
from dbus import PROPERTIES_IFACE
from dbus.service import BusName, Object as DBusObject, method as DBusMethod
from JobService import DBUS_JOB_IFACE, JobException

log = logging.getLogger('jobservice')

class SingleJobService(DBusObject):
    """Export a single job as its own object on our bus."""
    
    def __init__(self, conn=None, object_path=None,
                 bus_name=None, name=None, root=None):
        DBusObject.__init__(self, conn, object_path, bus_name)
        self.name = name
        self.root = root
        self.path = self.__dbus_object_path__
        self._props = {}
    
    @DBusMethod(PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        self.root.idle.ping()
        if interface != DBUS_JOB_IFACE:
            raise JobException('Interface not supported.')
        self._load_properties()
        return self._props
            
    @DBusMethod(PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        self.root.idle.ping()
        if interface != DBUS_JOB_IFACE:
            raise JobException('Interface not supported.')
        self._load_properties()
        return self._props[prop]
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def Start(self, sender=None, conn=None):
        """Start a job by name. Does not enable/disable the job."""
        self.root.idle.ping()
        log.debug('Start called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.start_service(self.name)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def Stop(self, sender=None, conn=None):
        """Stop a job by name. Does not enable/disable the job."""
        self.root.idle.ping()
        log.debug('Stop called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.stop_service(self.name)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='b', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def SetAutomatic(self, auto, sender=None, conn=None):
        """Make a job automatic or manual. Does not change state."""
        self.root.idle.ping()
        log.debug('SetAutomatic ({1}) called on {0}'.format(self.name, auto))
        self.root.policy.check(sender, conn)
        self.root.proxy.set_service_automatic(self.name, auto)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='s',
                out_signature='a(ssssa(ss)a{ss})',
                sender_keyword='sender', connection_keyword='conn')
    def GetSettings(self, lang, sender=None, conn=None):
        """
        Return a job's available settings and constraints.
        
        Takes a single argument (locale) used to determine what language the
        descriptions should be sent in. If unknown, use an empty string.
        
        Returns list of struct settings (
            string name
            string type
            string description
            string current-value
            list of struct values (
                string name
                string description
            )
            dict constraints {
                key: string type
                value: string value
            }
        )
        """
        self.root.idle.ping()
        log.debug('GetSettings ({1}) called on {0}'.format(self.name, lang))
        return self.root.proxy.get_service_settings(self.name, lang)
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='a{ss}', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def SetSettings(self, settings, sender=None, conn=None):
        """Change a job's settings after validating."""
        self.root.idle.ping()
        log.debug('SetSettings called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.set_service_settings(self.name, settings)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='ss', out_signature='b',
                sender_keyword='sender', connection_keyword='conn')
    def ValidateSetting(self, setting, value, sender=None, conn=None):
        """Verify a setting's value is valid."""
        self.root.idle.ping()
        log.debug('ValidateSetting ({1}) called on {0}'.format(self.name, setting))
    
    def _load_properties(self):
        if not self._props:
            self._props = self.root.proxy.get_service(self.name)
        
