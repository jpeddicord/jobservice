
from dbus import PROPERTIES_IFACE
from dbus.service import BusName, Object as DBusObject, method as DBusMethod
from JobService import DBUS_JOB_IFACE, JobException


class SingleJobService(DBusObject):
    """
    Exports a single job as its own object on our bus.
    """
    
    @DBusMethod(PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface == DBUS_IFACE:
            pass
        else:
            raise JobException('Interface not supported.')
            
    @DBusMethod(PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def GetAll(self, interface, prop):
        if interface == DBUS_IFACE:
            pass
        else:
            raise JobException('Interface not supported.')

    @DBusMethod(PROPERTIES_IFACE, in_signature='ssv', out_signature='')
    def Set(self, interface, prop, value):
        if interface == DBUS_IFACE:
            pass
        else:
            raise JobException('Interface not supported.')
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='s', out_signature='(ssssbbasasai)',
                sender_keyword='sender', connection_keyword='conn')
    def GetJob(self, jobname, sender=None, conn=None):
        """
        Returns a single job with additional details.
        
        Returns struct (
            string name
            string description
            string version
            string author
            boolean running
            boolean automatic
            array of string dependencies
            array of string dependants
            array of int active-runlevels
        )
        """
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='s', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def StartJob(self, jobname, sender=None, conn=None):
        """
        Starts a job by name.
        """
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='s', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def StopJob(self, jobname, sender=None, conn=None):
        """
        Stops a job by name.
        """
        pass
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='s', out_signature='a{s(ssss)}',
                sender_keyword='sender', connection_keyword='conn')
    def GetJobSettings(self, jobname, sender=None, conn=None):
        """
        Returns a job's available settings and constraints.
        
        Returns dictioniary {
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
    
    @DBusMethod(DBUS_JOB_IFACE, in_signature='sa{s(ssss)}', out_signature='',
                sender_keyword='sender', connection_keyword='conn')
    def SetJobSettings(self, jobname, settings, sender=None, conn=None):
        """
        Sets a job's settings.
        """
        pass
