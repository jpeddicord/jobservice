
from dbus import DBusException


DBUS_IFACE = 'com.ubuntu.JobService'
DBUS_PATH = '/com/ubuntu/JobService'
DBUS_JOB_IFACE = '{0}.Job'.format(DBUS_IFACE)

class JobException(DBusException):
    _dbus_error_name = '{0}.JobException'.format(DBUS_IFACE)
