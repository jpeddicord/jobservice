
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
            log.warn("Not enforcing PolicyKit privileges!")
    
    def check(self, sender, conn, priv='com.ubuntu.jobservice.manage'):
        """
        Check or ask for authentication for job management.
        """
        if not self.enforce: return
        log.debug("Asking for PolicyKit authorization")
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
            log.info("Authorization failed")
            raise DeniedByPolicy('Not authorized to manage jobs.')
        log.debug("Authorization passed")
        
            
