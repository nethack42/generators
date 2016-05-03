#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Golang Generator
Copyright (C) 2015 Patrick Pacher <patrick.pacher@gmail.com>

c_common.py: Common Library for generation of C/C++ bindings and documentation

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

class GoPacket(common.Packet):
    def get_go_parameter_list(self):
        param = ''
        setList = ''

        for element in self.get_elements():
            go_type = element.get_go_type(True)
            name = element.get_upper_case_name()
            pointer = ''
            arr = ''

            if element.get_direction() == 'out':
                continue
                #pointer = '*'
                #name = 'ret_{0}'.format(name)
            if element.get_cardinality() > 1:
                arr = '[{0}]'.format(element.get_cardinality())
                pointer = ''

            if param == "":
                param += '{0} {1}{2}{3}'.format(name, pointer, arr, go_type)
                setList += '{0}'.format(name)
            else:
                param += ', {0} {1}{2}{3}'.format(name, pointer, arr, go_type)
                setList += ', {0}'.format(name)

        return param, setList

    def get_go_return_list(self):
        param = ''
        loadList = ''

        for element in self.get_elements():
            go_type = element.get_go_type(True)
            name = element.get_camel_case_name()
            arr = ''
            pointer = '&'

            if element.get_direction() != 'out':
                continue
            if element.get_cardinality() > 1:
                arr = '[{0}]'.format(element.get_cardinality())
                pointer = ''

            if param == "":
                param += '{0} {1}{2}'.format(name, arr, go_type)
                loadList += '{0}{1}'.format(pointer, name)
            else:
                param += ', {0} {1}{2}'.format(name, arr, go_type)
                loadList += ', {0}{1}'.format(pointer, name)

        if param == "":
            param += 'err error'
        else:
            param += ', err error'

        return '(' + param + ')', loadList

class GoElement(common.Element):
    def get_go_type(self, is_in_signature):
        if self.get_type() == 'string':
            return 'byte'
        if self.get_type() == 'bool':
            return 'bool'
        if self.get_type() == 'char':
            return 'rune'
        if self.get_type() == 'float':
            return 'float64'
        #if self.get_type() in ('int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64'):
        #    return '{0}'.format(self.get_type())

        return self.get_type()
