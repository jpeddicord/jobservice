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

from dbus import DBusException

try:
    from JobService.info import prefix
except:
    prefix = '/usr'

DBUS_IFACE = 'com.ubuntu.JobService'
DBUS_PATH = '/com/ubuntu/JobService'
DBUS_JOB_IFACE = DBUS_IFACE + '.Job'

SLS_SYSTEM = prefix + '/share/jobservice/sls/{0}.xml'
SLS_DEFAULT = prefix + '/share/jobservice/default/{0}.xml'
SLS_LOCAL = None

class JobException(DBusException):
    _dbus_error_name = DBUS_IFACE + '.JobException'
    

