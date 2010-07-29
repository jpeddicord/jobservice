
from dbus import DBusException

try:
    from JobService.info import prefix
except:
    prefix = '/usr'

DBUS_IFACE = 'com.ubuntu.JobService'
DBUS_PATH = '/com/ubuntu/JobService'
DBUS_JOB_IFACE = '{0}.Job'.format(DBUS_IFACE)

SLS_SYSTEM = prefix + '/share/jobservice/sls/{0}.xml'
SLS_DEFAULT = prefix + '/share/jobservice/default/{0}.xml'
SLS_LOCAL = None

class JobException(DBusException):
    _dbus_error_name = DBUS_IFACE + '.JobException'
    

