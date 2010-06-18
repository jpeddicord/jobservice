
from os.path import exists
from xml.dom.minidom import parse

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
        self.dom = parse(self.filename)
        self.setting_nodes = {}
    
    def get_all_settings(self):
        """
        Return a list of setting names available on this service.
        """
        lst = []
        for s in self.dom.getElementsByTagName('setting'):
            name = s.getAttribute('name')
            self.setting_nodes[name] = s
            lst.append(name)
        return lst
    
    def get_setting(self, name):
        """
        Return details of a specific setting by name in the format
        (type, description, current value, possible values)
        """
        node = self.setting_nodes[name]
        current = "" #TODO
        # get available values
        values = []
        for v in node.getElementsByTagName('value'):
            values.append((v.getAttribute('name'),
                    v.getAttribute('description')))
        return (node.getAttribute('type'),
                node.getElementsByTagName('description')[0].firstChild.nodeValue,
                current, values)
    
    def set_values(self, name, values):
        pass
