# HID Report Descriptor Reader class
#
# Copyright (C) 2019 Ravikiran Bukkasagara <contact@ravikiranb.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# TAB = 4 spaces

import usb.core
import usb.util

import threading

_USB_HID_CLASS_CTRL_bmRequestType = 0x21
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_INPUT = 0x01 << 8
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_OUTPUT = 0x02 << 8
_USB_HID_CLASS_CTRL_wValue_REPORT_TYPE_FEATURE = 0x03 << 8

_USB_CLASS_bmRequestType_GET_DESCRIPTOR = 0x81
_USB_CLASS_bRequest_GET_DESCRIPTOR = 6
_USB_CLASS_wValue_GET_HID_REPORT_DESCRIPTOR = (0x22) << 8 # Report Descriptor

_USB_HID_CLASS_REPORT_DESCRIPTOR_TYPE = 0x22


_HID_ITEM_TAG_START_COLLECTION = 0xa
_HID_ITEM_TAG_END_COLLECTION = 0xc
_hid_item_size_index = [0, 1, 2, 4]

_hid_item_type_tag_index = {
            # Main
            0x0: {
                0x8: 'Input',
                0x9: 'Output',
                0xb: 'Feature',
                _HID_ITEM_TAG_START_COLLECTION: 'Collection',
                _HID_ITEM_TAG_END_COLLECTION: 'End Collection',
                },
            # Global
            0x1: {
                0x0: 'Usage Page',
                0x1: 'Logical Minimum',
                0x2: 'Logical Maximum',
                0x3: 'Physical Minimum',
                0x4: 'Physical Maximum',
                0x5: 'Unit Exponent',
                0x6: 'Unit',
                0x7: 'Report Size',
                0x8: 'Report ID',
                0x9: 'Report Count',
                0xa: 'Push',
                0xb: 'Pop',
                },
            # Local
            0x2: {
                0x0: 'Usage',
                0x1: 'Usage Minimum',
                0x2: 'Usage Maximum',
                0x3: 'Designator Index',
                0x4: 'Designator Minimum',
                0x5: 'Designator Maximum',
                0x7: 'String Index',
                0x8: 'String Minimum',
                0x9: 'String Maximum',
                0xa: 'Delimiter',
                },
            }


class HIDReportDescriptorReader:
    """Read and parse Report Descriptor in human readable format.
    
    Issues GET_DESCRIPTOR class control request to read Report descriptor.
    Long items are not implemented.
    Usage Pages and Usages are not yet mapped to readable names.
    """
    
    def __init__(self, device, interface):
        
        kernel_driver_was_active = device.is_kernel_driver_active(interface.bInterfaceNumber)
        if kernel_driver_was_active:
            device.detach_kernel_driver(interface.bInterfaceNumber)
            
        try:
            desc_bytes = interface.extra_descriptors
            # bNumDescriptors - offset 5 in HID Descriptor
            # bDescriptorType - offset 6 in HID Descriptor
            # wDescriptorLength - offset 7 in HID Descriptor
            n_descriptors = desc_bytes[5] 
            self.report_descriptor = None
            for d in range(n_descriptors):
                desc_type = desc_bytes[6 + (d*3)]
                desc_length = desc_bytes[7 + (d*3)] | (desc_bytes[8 + (d*3)])
                if desc_type == _USB_HID_CLASS_REPORT_DESCRIPTOR_TYPE:
                    self.report_descriptor = device.ctrl_transfer(_USB_CLASS_bmRequestType_GET_DESCRIPTOR,
                                _USB_CLASS_bRequest_GET_DESCRIPTOR,
                                _USB_CLASS_wValue_GET_HID_REPORT_DESCRIPTOR,
                                interface.bInterfaceNumber,
                                desc_length)
                    break
        finally:    
            usb.util.dispose_resources(device)
            if kernel_driver_was_active:
                device.attach_kernel_driver(interface.bInterfaceNumber)

    def __str__(self):
        if self.report_descriptor is None:
            return ""

        items = []
        i = 0
        s = ""
        n_collections = 0
        while i < len(self.report_descriptor): 
            prefix = self.report_descriptor[i]
            if prefix == 0xFE:
                raise Exception("HID report parser: Long items are not implemented.")
            i += 1
            size = prefix & 0x3
            itype = (prefix >> 2) & 0x3
            tag = (prefix >> 4) & 0xf
            
            if itype == 0 and tag == _HID_ITEM_TAG_START_COLLECTION:
                s += ('  ' * n_collections) + _hid_item_type_tag_index[itype][tag]
                n_collections += 1
            else:
                if itype == 0 and tag == _HID_ITEM_TAG_END_COLLECTION:
                    n_collections -= 1
                s += ('  ' * n_collections) + _hid_item_type_tag_index[itype][tag]
            
            
            if _hid_item_size_index[size] > 0:
                s += '('
                value = 0
                for j in range(_hid_item_size_index[size]):
                    value |= self.report_descriptor[i+j] << (j*8)
                s += hex(value) + ')'
                
            s += '\n'
            i += _hid_item_size_index[size]
        
        return s
