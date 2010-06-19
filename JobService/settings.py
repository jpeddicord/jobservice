
from os.path import exists
from xml.etree.cElementTree import ElementTree

SLS_SYSTEM = '/usr/share/jobservice/sls/{0}.xml'
SLS_LOCAL = 'sls/{0}.xml'


class ServiceSettings:
    """
    Manages service-level settings (SLS) for a single service.
    """
    
    def __init__(self, jobname):
        self.jobname = jobname
        self.filename = SLS_SYSTEM.format(jobname)
        if not exists(self.filename):
            self.filename = SLS_LOCAL.format(jobname)
        self.tree = ElementTree()
        self.tree.parse(self.filename)
        self.selements = {}
    
    def get_all_settings(self):
        """
        Return a list of setting names available on this service.
        """
        lst = []
        for e in self.tree.findall('setting'):
            name = e.get('name')
            self.selements[name] = e
            lst.append(name)
        return lst
    
    def get_setting(self, name):
        """
        Return details of a specific setting by name in the format
        (type, description, current value, possible values)
        """
        ele = self.selements[name]
        raw = self._get_raw_value(ele)
        # get available values
        values = []
        current = raw
        for v in ele.findall('values/value'):
            values.append((v.get('name'), v.get('description', '')))
            if v.text == raw:
                current = v.get('name')
        print current
        return (ele.get('type'), ele.findtext('description'), current, values)
    
    def set_values(self, name, values):
        pass
    
    def _get_raw_value(self, ele):
        before, after = ele.findtext('parse').strip().split('%s')
        value = False
        with open(ele.findtext('file')) as f:
            for line in f:
                beforepos = line.find(before)
                # the second check is to make sure this is the right line,
                # but we only perform it if we _might_ have it for speed.
                if beforepos >= 0 and line.strip().find(before) == 0:
                    start = beforepos + len(before)
                    if after:
                        value = line[start:line.find(after, start)]
                    else:
                        value = line[start:len(line)-1] # \n at the end
                    break
        return value
