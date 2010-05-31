
from dbus import PROPERTIES_IFACE
from dbus.service import BusName, Object as DBusObject, method as DBusMethod
from JobService import DBUS_JOB_IFACE, JobException


class SingleJobService(DBusObject):
    """
    Exports a single job as its own object on our bus.
    """
    
    def __init__(self, conn=None, object_path=None, bus_name=None, name=None, proxy=None, running=False):
        DBusObject.__init__(self, conn, object_path, bus_name)
        
        self.name = name
        self.proxy = proxy
        self.running = running
        self.path = self.__dbus_object_path__
        self._props = {}
    
    @DBusMethod(PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface == DBUS_JOB_IFACE:
            self._load_properties()
            return self._props
        else:
            raise JobException('Interface not supported.')
            
    @DBusMethod(PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
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
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def Stop(self, sender=None, conn=None):
        """
        Stops a job by name.
        """
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='', out_signature='a{s(ssss)}',
                sender_keyword='sender', connection_keyword='conn')
    def GetSettings(self, sender=None, conn=None):
        """
        Returns a job's available settings and constraints.
        
        Returns dict {
            key: string setting-name
            value: struct (
                string name
                string description
                string value
                string type
            )
        }
        """
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='a{s(ssss)}', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def SetSettings(self, settings, sender=None, conn=None):
        """
        Sets a job's settings.
        """
        pass
    
    def _load_properties(self):
        if not self._props:
            self._props = self.proxy.get_service(self.name)
        
