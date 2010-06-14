

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
            #safe += '_%02x' % ord(ch)
            safe += '_{0:02x}'.format(ord(ch))
    return safe
