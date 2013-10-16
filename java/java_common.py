#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Java Documentation Generator
Copyright (C) 2012-2013 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011-2013 Olaf Lüke <olaf@tinkerforge.com>

java_common.py: Common Library for generation of Java bindings and documentation

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys
import os

sys.path.append(os.path.split(os.getcwd())[0])
import common

def get_object_name(packet):
    name = packet.get_camel_case_name()
    if name.startswith('Get'):
        name = name[3:]

    return name

def get_return_type(packet, for_doc=False):
    elements = packet.get_elements('out')

    if len(elements) == 0:
        return 'void'

    if len(elements) > 1:
        if for_doc:
            return packet.get_device().get_category() + packet.get_device().get_camel_case_name() + '.' + get_object_name(packet)
        else:
            return get_object_name(packet)

    return_type = elements[0].get_java_type()

    if elements[0].get_cardinality() > 1 and elements[0].get_type() != 'string':
        return_type += '[]'

    return return_type

def make_parameter_list(packet, just_types=False):
    param = []
    for element in packet.get_elements():
        if element.get_direction() == 'out' and packet.get_type() == 'function':
            continue
        java_type = element.get_java_type()
        name = element.get_headless_camel_case_name()
        arr = ''
        if element.get_cardinality() > 1 and element.get_type() != 'string':
            arr = '[]'

        if just_types:
            param.append('{0}{1}'.format(java_type, arr))
        else:
            param.append('{0}{1} {2}'.format(java_type, arr, name))
    return ', '.join(param)

class JavaDevice(common.Device):
    def get_java_class_name(self):
        return self.get_category() + self.get_camel_case_name()

class JavaElement(common.Element):
    java_type = {
        'int8':   'byte',
        'uint8':  'short',
        'int16':  'short',
        'uint16': 'int',
        'int32':  'int',
        'uint32': 'long',
        'int64':  'long',
        'uint64': 'long',
        'float':  'float',
        'bool':   'boolean',
        'string': 'String',
        'char':   'char'
    }

    java_byte_buffer_method_suffix = {
        'int8':   '',
        'uint8':  '',
        'int16':  'Short',
        'uint16': 'Short',
        'int32':  'Int',
        'uint32': 'Int',
        'int64':  'Long',
        'uint64': 'Long',
        'float':  'Float',
        'bool':   '',
        'string': '',
        'char':   ''
    }

    java_byte_buffer_storage_type = {
        'int8':   'byte',
        'uint8':  'byte',
        'int16':  'short',
        'uint16': 'short',
        'int32':  'int',
        'uint32': 'int',
        'int64':  'long',
        'uint64': 'long',
        'float':  'float',
        'bool':   'byte',
        'string': 'byte',
        'char':   'byte'
    }

    def get_java_type(self):
        return JavaElement.java_type[self.get_type()]

    def get_java_byte_buffer_method_suffix(self):
        return JavaElement.java_byte_buffer_method_suffix[self.get_type()]

    def get_java_byte_buffer_storage_type(self):
        return JavaElement.java_byte_buffer_storage_type[self.get_type()]
