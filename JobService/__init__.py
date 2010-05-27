
from dbus import DBusException


DBUS_IFACE = 'com.ubuntu.JobService'
DBUS_PATH = '/com/ubuntu/JobService'
DBUS_JOB_IFACE = '%s.Job' % DBUS_IFACE

class JobException(DBusException):
    _dbus_error_name = '%s.JobException' % DBUS_IFACE
