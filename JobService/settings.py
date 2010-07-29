
import logging
from os import rename
from os.path import exists
from xml.etree.cElementTree import ElementTree
import JobService

log = logging.getLogger('sls')

class ServiceSettings:
    """Service-level settings (SLS) for a single service."""
    
    def __init__(self, jobname):
        self.jobname = jobname
        self.filename = ''
        for loc in (JobService.SLS_LOCAL, JobService.SLS_SYSTEM, JobService.SLS_DEFAULT):
            if not loc:
                continue
            self.filename = loc.format(jobname)
            if exists(self.filename):
                log.debug('Using ' + self.filename)
                break
        self.tree = ElementTree()
        self.tree.parse(self.filename)
        self.selements = {}
        self.settings = {}
    
    def get_all_settings(self):
        """Return a list of setting names available on this service."""
        lst = []
        for e in self.tree.findall('setting'):
            name = e.get('name')
            self.selements[name] = e
            lst.append(name)
        return lst
    
    def get_setting(self, name, lang=''):
        """Return details of a specific setting by name in the format:
        (name, type, description, current value, possible values[],
                constraints{})
        """
        ele = self.selements[name]
        # current value
        raw = ""
        data = ele.find('data')
        if data != None:
            fixed = data.get('val')
            if fixed:
                raw = fixed
            else:
                for p in ele.findall('data/parse'):
                    fname = p.get('file')
                    if fname:
                        with open(fname) as f:
                            raw = self._raw_value(p.text, f)
        # get available values
        values = []
        self.settings[name] = raw
        for v in ele.findall('values/value'):
            values.append((v.get('name'), v.findtext('description', '')))
            if v.findtext('raw') == raw:
                self.settings[name] = v.get('name')
        vals = ele.find('values')
        constraints = vals.attrib if vals != None else {}
        return (name, ele.get('type'), ele.findtext('description'),
                self.settings[name], values, constraints)
    
    def set_setting(self, name, value):
        ele = self.selements[name]
        # don't do anything with an empty data element
        data = ele.find('data')
        if not len(data):
            return
        # translate the value into something for the file
        newval = value
        for v in ele.findall('values/value'):
            if v.get('name') == value:
                newval = v.findtext('raw')
                break
        # write out values
        for p in data.findall('parse'):
            # write to file
            if p.get('file'):
                filename = p.get('file')
                # write the new values
                read = open(filename)
                write = open('{0}.new'.format(filename), 'w')
                self._raw_value(p.text, read, write, newval)
                write.close()
                read.close()
                # replace the original with backup
                rename(read.name, '{0}~'.format(read.name))
                rename(write.name, read.name)
            # send to an external program for processing
            elif p.get('set'):
                pass #TODO
    
    def _raw_value(self, parse, read, write=None, newval=None):
        """
        Read or write (if write is not None) a raw value to a conf file.
        read & write are file objects.
        """
        assert parse
        before, after = parse.strip().split('%s')
        value = False
        for line in read:
            beforepos = line.find(before)
            # the second check is to make sure this is the right line,
            # but we only perform it if we _might_ have it for speed.
            if beforepos >= 0 and line.strip().find(before) == 0:
                if write:
                    write.write(''.join((line[:beforepos],
                            before, newval, after, '\n')))
                else:
                    start = beforepos + len(before)
                    if after:
                        value = line[start:line.find(after, start)]
                    else:
                        value = line[start:len(line)-1] # \n at the end
                    return value
                continue
            if write:
                write.write(line)
        
