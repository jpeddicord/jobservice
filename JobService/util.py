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
from time import time
from glib import timeout_add_seconds

log = logging.getLogger('jobservice')

class IdleTimeout:
    """
    Keeps track of the time since last use.
    If idle for too long, quit.
    """
    
    def __init__(self, loop, idlemax):
        self.loop = loop
        self.idlemax = idlemax
        self.lastused = time()
        self.timeout = timeout_add_seconds(idlemax, self.callback)
        
    def callback(self):
        now = time()
        # we were left idle, time to quit
        if now - self.lastused > self.idlemax:
            log.info("Left idle - shutting down")
            self.loop.quit()
            return False
        return True
    
    def ping(self):
        self.lastused = time()

def dbus_safe_name(unsafe):
    """
    Returns a name that is safe to export over DBus.
    Based on the implementation in upstart/libnih.
    """
    safe = ''
    for ch in unsafe:
        if (ch >= 'a' and ch <= 'z') or (ch >= 'a' and ch <= 'z') or (ch >= '0' and ch <= '9'):
            safe += ch
        else:
            safe += '_{0:02x}'.format(ord(ch))
    return safe


