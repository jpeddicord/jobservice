
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


