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

from os.path import exists
from dbus import DBusException


class ValidationError(DBusException):
    _dbus_error_name = 'com.ubuntu.JobService.ValidationError'

class Type:
    """Root type."""
    def __init__(self, values, constraints):
        self.values = values
        self.constraints = constraints
    
    def validate(self):
        return
    
    def clean(self, data):
        return data

class Bool(Type):
    """A boolean accepting "true" and "false" literal values."""
    def validate(self, data):
        if data not in ('true', 'false'):
            raise ValidationError("Invalid boolean value.")

class Int(Type):
    """An integer with optional constraints."""
    convert = int
    def validate(self, data):
        print convert
        if 'min' in self.constraints and convert(data) < convert(self.constraints['min']):
            raise ValidationError("Out of bounds.")
        if 'max' in self.constraints and convert(data) > convert(self.constraints['max']):
            raise ValidationError("Out of bounds.")

class Float(Int):
    """A floating-point. Same constraints as Int."""
    convert = float

class Str(Type):
    """A string."""
    pass

class Label(Type):
    """A graphical label. Contains no data."""
    pass

class Choice(Type):
    """A choice out of a finite set of options."""
    def validate(self, data):
        if data not in self.values.keys():
            raise ValidationError("Not a valid choice.")

class File(Type):
    """A single file path."""
    def validate(self, data):
        if 'exists' in self.constraints and self.constraints['exists'] == 'true':
            if not os.path.exists(data):
                raise ValidationError("File does not exist.")

class Dir(File):
    """A path to a directory."""
    pass

class User(Type):
    """A user on the system."""
    pass

class Group(Type):
    """A group on the system."""
    pass

class Exec(Type):
    """Special action to suggest that another program should be used."""
    pass
