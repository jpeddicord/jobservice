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
from os import rename
from os.path import exists
from cStringIO import StringIO
from subprocess import Popen, PIPE
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
        (name, type, description, current, possible[], constraints{})
        """
        ele = self.selements[name]
        # current value
        raw = ''
        data = ele.find('data')
        if data != None:
            fixed = data.get('val')
            if fixed:
                raw = fixed
            else:
                # find the first source we can obtain a value from
                for p in ele.findall('data/parse'):
                    parse = p.text.replace('%n', name)
                    # load from file
                    if p.get('file'):
                        prescan = p.get('after')
                        with open(p.get('file')) as f:
                            raw = self._raw_value(parse, f, prescan=prescan)
                        break
                    # load from external helper
                    elif p.get('get'):
                        proc = Popen(p.get('get'), shell=True, stdout=PIPE)
                        sio = StringIO(proc.communicate()[0])
                        raw = self._raw_value(parse, sio)
                        break
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
            parse = p.text.replace('%n', name)
            # write to file
            if p.get('file'):
                filename = p.get('file')
                prescan = p.get('after')
                # write the new values
                read = open(filename)
                write = open('{0}.new'.format(filename), 'w')
                self._raw_value(parse, read, write, newval, prescan)
                write.close()
                read.close()
                # replace the original with backup
                rename(read.name, '{0}~'.format(read.name))
                rename(write.name, read.name)
            # send to an external program for processing
            elif p.get('set'):
                proc = Popen(p.get('set'), shell=True, stdin=PIPE)
                proc.communicate(parse.replace('%s', newval))
    
    def _raw_value(self, parse, read, write=None, newval=None, prescan=None):
        """
        Read or write (if write is not None) a raw value to a conf file.
        read & write are file objects.
        
        If the setting line has been commented, it will still be read normally.
        On write, the comment will be removed. Default settings are assumed
        to be commented out, so when changing them we'll need to uncomment.
        
        If "prescan" is set, will not begin scanning until the string provided
        has been passed.
        """
        assert parse
        before, after = parse.strip().split('%s')
        value = False
        scanning = False if prescan else True
        for line in read:
            if not scanning and prescan:
                if line.find(prescan) != -1:
                    scanning = True
            beforepos = line.find(before)
            # the last check is to make sure this is the right line,
            # but we only perform it if we _might_ have it for speed.
            if scanning and beforepos >= 0 and line.lstrip(' #;\t').find(before) == 0:
                if write:
                    data = ''.join((line[:beforepos], before, newval, after, '\n'))
                    write.write(data.lstrip('#;'))
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
        return ''
