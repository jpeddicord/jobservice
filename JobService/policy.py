
from dbus import SystemBus, DBusException, Interface


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
    
    def check(self, sender, conn, priv='com.ubuntu.jobservice.manage'):
        """
        Check or ask for authentication for job management.
        """
        if not self.enforce: return
        # get the PID of the sender
        if not self.dbus_iface:
            self.dbus_iface = Interface(conn.get_object('org.freedesktop.DBus',
                    '/org/freedesktop/DBus/Bus'), 'org.freedesktop.DBus')
        pid = self.dbus_iface.GetConnectionUnixProcessID(sender)
        # ask PolicyKit
        auth, challenge, details = self.pk.CheckAuthorization(
                ('unix-process', {'pid': pid, 'start-time': 0}),
                priv, {'': ''}, 1, '')
        if not auth:
            raise DeniedByPolicy('Not authorized to manage jobs.')
        
            
