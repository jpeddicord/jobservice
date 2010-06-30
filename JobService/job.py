
import logging
from dbus import PROPERTIES_IFACE
from dbus.service import BusName, Object as DBusObject, method as DBusMethod
from JobService import DBUS_JOB_IFACE, JobException

log = logging.getLogger('jobservice')

class SingleJobService(DBusObject):
    """
    Exports a single job as its own object on our bus.
    """
    
    def __init__(self, conn=None, object_path=None, bus_name=None, name=None, root=None):
        DBusObject.__init__(self, conn, object_path, bus_name)
        
        self.name = name
        self.root = root
        self.path = self.__dbus_object_path__
        self._props = {}
    
    @DBusMethod(PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        self.root.idle.ping()
        if interface == DBUS_JOB_IFACE:
            self._load_properties()
            return self._props
        else:
            raise JobException('Interface not supported.')
            
    @DBusMethod(PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        self.root.idle.ping()
        if interface == DBUS_JOB_IFACE:
            self._load_properties()
            return self._props[prop]
        else:
            raise JobException('Interface not supported.')
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def Start(self, sender=None, conn=None):
        """
        Starts a job by name.
        """
        self.root.idle.ping()
        log.debug('Start called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.start_service(self.name)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def Stop(self, sender=None, conn=None):
        """
        Stops a job by name.
        """
        self.root.idle.ping()
        log.debug('Stop called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.stop_service(self.name)
        self._props = {}
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='a{s(sssa(ss)a{ss})}',
                sender_keyword='sender', connection_keyword='conn')
    def GetSettings(self, sender=None, conn=None):
        """
        Returns a job's available settings and constraints.
        
        Returns dict settings {
            key: string setting-name
            value: struct (
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
        }
        """
        self.root.idle.ping()
        log.debug('GetSettings called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        return self.root.proxy.get_service_settings(self.name)
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='a{ss}', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def SetSettings(self, settings, sender=None, conn=None):
        """
        Sets a job's settings.
        """
        self.root.idle.ping()
        log.debug('SetSettings called on {0}'.format(self.name))
        self.root.policy.check(sender, conn)
        self.root.proxy.set_service_settings(self.name, settings)
    
    def _load_properties(self):
        if not self._props:
            self._props = self.root.proxy.get_service(self.name)
        
