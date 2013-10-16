#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
C# Documentation Generator
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

csharp_common.py: Common Library for generation of C# bindings and documentation

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

import os
import sys

sys.path.append(os.path.split(os.getcwd())[0])
import common

def make_parameter_list(packet, useOutParams=True):
    param = []
    for element in packet.get_elements():
        if (not useOutParams) and element.get_direction() == 'out':
            continue

        out = ''
        if element.get_direction() == 'out' and packet.get_type() == 'function':
            out = 'out '

        csharp_type = element.get_csharp_type()
        name = element.get_headless_camel_case_name()

        param.append('{0}{1} {2}'.format(out, csharp_type, name))
    return ', '.join(param)

def make_method_signature(packet, printFullName=False, device=None, is_doc=False):
    sig_format = "public {4}{0} {1}{2}({3})"
    ret_count = len(packet.get_elements('out'))
    params = make_parameter_list(packet, ret_count > 1)
    return_type = 'void'
    if ret_count == 1:
        return_type = packet.get_elements('out')[0].get_csharp_type()
    classPrefix = ''
    if printFullName:
        classPrefix = device.get_category() + device.get_camel_case_name() + '::'
    override = ''
    if not is_doc and packet.has_prototype_in_device():
        override = 'override '

    return sig_format.format(return_type, classPrefix, packet.get_camel_case_name(), params, override)

class CSharpDevice(common.Device):
    def get_csharp_class_name(self):
        return self.get_category() + self.get_camel_case_name()

class CSharpElement(common.Element):
    csharp_types = {
        'int8':   'short',
        'uint8':  'byte',
        'int16':  'short',
        'uint16': 'int',
        'int32':  'int',
        'uint32': 'long',
        'int64':  'long',
        'uint64': 'long',
        'float':  'float',
        'bool':   'bool',
        'string': 'string',
        'char':   'char'
    }

    csharp_le_converter_types = {
        'int8':   'byte',
        'uint8':  'byte',
        'int16':  'short',
        'uint16': 'short',
        'int32':  'int',
        'uint32': 'int',
        'int64':  'long',
        'uint64': 'long',
        'float':  'float',
        'bool':   'bool',
        'string': 'string',
        'char':   'char'
    }

    csharp_le_converter_from_methods = {
        'int8':   'SByteFrom',
        'uint8':  'ByteFrom',
        'int16':  'ShortFrom',
        'uint16': 'UShortFrom',
        'int32':  'IntFrom',
        'uint32': 'UIntFrom',
        'int64':  'LongFrom',
        'uint64': 'ULongFrom',
        'float':  'FloatFrom',
        'bool':   'BoolFrom',
        'string': 'StringFrom',
        'char':   'CharFrom'
    }

    def get_csharp_type(self):
        t = CSharpElement.csharp_types[self.get_type()]

        if self.get_cardinality() > 1 and self.get_type() != 'string':
            t += '[]'

        return t

    def get_csharp_le_converter_type(self):
        t = CSharpElement.csharp_le_converter_types[self.get_type()]

        if self.get_cardinality() > 1 and self.get_type() != 'string':
            t += '[]'

        return t

    def get_csharp_le_converter_from_method(self):
        m =  CSharpElement.csharp_le_converter_from_methods[self.get_type()]

        if m != 'StringFrom' and self.get_cardinality() > 1:
            m = m.replace('From', 'ArrayFrom')

        return m
