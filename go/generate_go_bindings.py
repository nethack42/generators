#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Golang Bindings Generator
Copyright (C) 2016 Patrick Pacher <patrick.pacher@gmail.com>

generate_go_bindings.py: Generator for Golang bindings

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
import go_common

class GoBindingsDevice(common.Device):
    def get_go_file_header(self):
        header = """{0}

package {1}

import "fmt"
import "git.ppacher.at/paz/go-tinkerforge"

type {2} struct {{
    *tinkerforge.Device
}}
"""
        package = self.get_camel_case_category() + self.get_camel_case_name()
        return header.format(self.get_generator().get_header_comment('asterisk'),
                                 package, self.get_camel_case_name())

    def get_go_function_id_defines(self):
        define_temp =  """
// Function{1} defines the function id for {1} on a {0} device
const Function{1} = {2}
"""

        defines = ''
        for packet in self.get_packets('function'):
            defines += define_temp.format(self.get_camel_case_name(),
                                          packet.get_camel_case_name(),
                                          packet.get_function_id(),
                                          self.get_camel_case_name(),
                                          self.get_camel_case_category())

        return defines

    def get_go_callback_defines(self):
        define_temp = """
// Callback{1} defines the function id for {1} on a {0} device
const Callback{1} = {2}
"""

        defines = ''
        for packet in self.get_packets('callback'):
            defines += define_temp.format(self.get_camel_case_name(),
                                          packet.get_camel_case_name(),
                                          packet.get_function_id())

        return defines

    def get_go_constants(self):
        constant_format = """
const {prefix}{constant_group_camel_case_name}{constant_camel_case_name} = {constant_value}
"""
        return '\n' + self.get_formatted_constants(constant_format,
                                                   doxygen=self.get_camel_case_category()+self.get_camel_case_name(),
                                                   prefix=self.get_camel_case_name())

    def get_go_device_identifier_define(self):
        define_temp = """
// DeviceIdentifier defines the ID of a {0}
const DeviceIdentifier = {1}
"""
        return define_temp.format(self.get_camel_case_name(),
                                  self.get_device_identifier(),
                                  self.get_camel_case_name(),
                                  self.get_camel_case_category(),
                                  self.get_underscore_name(),
                                  self.get_long_display_name())

    def get_go_device_display_name_define(self):
        define_temp = """
// DeviceDisplayName defines the device name of {0} as a string
const DeviceDisplayName = "{1}"
"""
        return define_temp.format(self.get_camel_case_name(),
                                  self.get_long_display_name(),
                                  self.get_camel_case_name(),
                                  self.get_camel_case_category())

    def get_go_create_function(self):
        function = """
func New{1} (uid tinkerforge.UID, ip *tinkerforge.IPConnection) *{1} {{
\t{0} := &{1}{{
\t\tDevice: tinkerforge.NewDevice(ip, uid, [3]byte{{{3}}}),
\t}}

{2}

\treturn {0}
}}
"""

        cb_temp = """
\t//device_p.callback_wrappers[{3}Callback{1}] = {0}_callback_wrapper_{2};"""

        cbs = ''
        dev_name = self.get_underscore_name()
        for packet in self.get_packets('callback'):
            type_name = packet.get_underscore_name()
            cbs += cb_temp.format(dev_name, type_name.upper(), type_name, dev_name.upper())

        response_expected = ''

        for packet in self.get_packets():
            if packet.get_type() == 'callback':
                prefix = 'Callback'
                flag = 'tinkerforge.NoResponseExpectedImmutable'
            elif len(packet.get_elements('out')) > 0:
                prefix = 'Function'
                flag = 'tinkerforge.ResponseIsExpectedImmutable'
            elif packet.get_doc_type() == 'ccf':
                prefix = 'Function'
                flag = 'tinkerforge.ResponseIsExpected'
            else:
                prefix = 'Function'
                flag = 'tinkerforge.NoResponseExpected'

            response_expected += '\t{0}.ResponseExpected[{2}{3}] = {4}\n' \
                .format(dev_name, self.get_camel_case_name(), prefix, packet.get_camel_case_name(), flag)

        if len(response_expected) > 0:
            response_expected = '\n' + response_expected

        return function.format(dev_name,
                               self.get_camel_case_name(),
                               response_expected + cbs,
                               *self.get_api_version())

    def get_go_destroy_function(self):
        function = """
func ({0} *{1}) Destroy() {{
\t// TODO
}}
"""
        return function.format(self.get_camel_case_name(),
                               self.get_camel_case_name())


    def get_go_functions(self):
        function_version = """
func ({0} *{1}) GetAPIVersion() [3]byte {{
\treturn {0}.Device.GetAPIVersion()
}}
"""

        function = """
func ({0} *{2}) {1} ({3}) {4}  {{

    p, err := {0}.NewPacket({5})
    if err != nil {{
        return
    }}

    if err = p.EncodePayload({6}); err != nil {{
        return
    }}

    res := {0}.SendPacket(p)
    if res != nil {{
        response := <- res

        if response.ErrorCode() != 0 {{
            err = fmt.Errorf("%d", response.ErrorCode())
            return
        }}

        if err = p.DecodePayload({7}); err != nil {{
            return
        }}
    }}
    return
}}
"""
        device_name = self.get_underscore_name()
        c = self.get_camel_case_name()

        functions = []
        for packet in self.get_packets('function'):
            packet_name = packet.get_camel_case_name()
            params, set_list = packet.get_go_parameter_list()
            return_list, load_list = packet.get_go_return_list()

            fid = 'Function{1}'.format(self.get_camel_case_name(),
                                            packet.get_camel_case_name())

            functions.append(function.format(device_name, packet_name, c, params, return_list, fid, set_list, load_list))

        return function_version.format(device_name, c) + ''.join(functions)

    def get_go_callback_wrapper_functions(self):
        function = """

func ({0} {1}) {2}Callback (handler, user interface{{}}, packet tinkerforge.Packet) {{
    if handler == nil {{
        return
    }}

    f := handler.({2}CallbackFunction)

    {3}

    if err := packet.DecodePayload({4}); err != nil {{
        // TODO: log some error here
        return
    }}

    f({5} user)
}}
"""

        functions = []
        for packet in self.get_packets('callback'):
            deviceVar = self.get_underscore_name()
            deviceClass = self.get_camel_case_name()

            wrapperName = packet.get_camel_case_name()

            return_list, load_list = packet.get_go_return_list()

            _var_list = return_list[1:-1].split(", ")[0:-1]
            var_list = ""

            for i in _var_list:
                var_list += "\tvar " + i + "\n"


            set_list = load_list.replace('&', '')
            if set_list != "":
                set_list += ", "

            functions.append(function.format(deviceVar, deviceClass, wrapperName, var_list, load_list, set_list))

        return ''.join(functions)


    def get_go_typedefs(self):
        typedef = """
type {0}CallbackFunction func({1});
"""

        typedefs = '\n'

        for packet in self.get_packets('callback'):
            name = packet.get_camel_case_name()
            go_type_list = []

            for element in packet.get_elements():
                if element.get_cardinality() > 1:
                    go_type_list.append('[{1}]{0}'.format(element.get_go_type(True), element.get_cardinality()))
                else:
                    go_type_list.append(element.get_go_type(True))

            typedefs += typedef.format(name, ', '.join(go_type_list + ['interface{}']))

        return typedefs

    def get_go_source(self):
        source  = self.get_go_file_header()
        source += self.get_go_typedefs()

        source += self.get_go_function_id_defines()
        source += self.get_go_callback_defines()
        source += self.get_go_constants()
        source += self.get_go_device_identifier_define()
        source += self.get_go_device_display_name_define()

        source += self.get_go_callback_wrapper_functions()
        source += self.get_go_create_function()
        source += self.get_go_destroy_function()
        source += self.get_go_functions()

        return source

class GoBindingsPacket(go_common.GoPacket):
    pass

class CBindingsGenerator(common.BindingsGenerator):
    def get_bindings_name(self):
        return 'go'

    def get_bindings_display_name(self):
        return 'Golang'

    def get_device_class(self):
        return GoBindingsDevice

    def get_packet_class(self):
        return GoBindingsPacket

    def get_element_class(self):
        return go_common.GoElement

    def generate(self, device):
        filename = '{0}_{1}'.format(device.get_underscore_category(), device.get_underscore_name())
        package = device.get_camel_case_category() + device.get_camel_case_name()

        dir = os.path.join(self.get_bindings_root_directory(), 'bindings', package)
        os.mkdir(dir)

        c = open(os.path.join(self.get_bindings_root_directory(), 'bindings', package, filename + '.go'), 'wb')
        c.write(device.get_go_source())
        c.close()

        if device.is_released():
            self.released_files.append(filename + '.go')

def generate(bindings_root_directory):
    common.generate(bindings_root_directory, 'en', CBindingsGenerator)

if __name__ == "__main__":
    generate(os.getcwd())
