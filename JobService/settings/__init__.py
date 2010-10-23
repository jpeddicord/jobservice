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
from os.path import exists
from JobService.settings.parser import SettingParser
import JobService

log = logging.getLogger('sls')

class ServiceSettings:
    """Service-level settings (SLS) for a single service."""
    
    def __init__(self, jobname):
        self.jobname = jobname
        if '/' in jobname:
            basename = jobname.split('/')[0]
        else:
            basename = jobname
        self.filename = ''
        for loc in (JobService.SLS_LOCAL, JobService.SLS_SYSTEM, JobService.SLS_DEFAULT):
            if not loc:
                continue
            self.filename = loc.format(basename)
            if exists(self.filename):
                log.debug('Using ' + self.filename)
                break
        self.settings = {}
        self.parser = SettingParser(self.filename, jobname)
    
    def get_all_settings(self):
        return self.parser.get_all_settings()
    
    def get_setting(self, name, lang=''):
        return self.parser.get_setting(name, lang)
    
    def set_setting(self, name, value):
        self.parser.set_setting(name, value)
