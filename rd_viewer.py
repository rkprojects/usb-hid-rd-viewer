# USB HID Report Descriptor Viewer
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

# Entry point module for the program

import textwrap
import threading
import argparse
import sys

import usb.core
import usb.util

version = "1.0"
program_desc = "USB HID Report Descriptor Viewer {0}".format(version)

from rd_reader import HIDReportDescriptorReader
HID_CLASS_bInterfaceClass = 0x3

def is_hid(dev):
        if dev.bDeviceClass == HID_CLASS_bInterfaceClass:
            return True
        for cfg in dev:
            if usb.util.find_descriptor(cfg, bInterfaceClass=HID_CLASS_bInterfaceClass) is not None:
                return True
        return False

def parse_user_device_id(dev_id_str):
    vid_pid = dev_id_str.strip()
    ids = vid_pid.split(':', maxsplit=2)
    if len(ids) != 2:
        raise Exception("Invalid device {0}".format(dev_id_str))
    # raises exception if not valid hex
    vid = int(ids[0], base=16)
    pid = int(ids[1], base=16)
    
    device = usb.core.find(idVendor=vid, idProduct=pid)
    if device is None:
        raise Exception("Device {0} not found".format(dev_id_str))
    
    if is_hid(device) == False:
        raise Exception("Device {0} has no HID class interface".format(dev_id_str))
    
    return device


def read_rd(hid, ofile_name):
    ofile = sys.stdout
    if ofile_name != '':
        ofile = open(ofile_name, 'w')

    try:
        cfg = hid.get_active_configuration()
        for intf in cfg:
            if intf.bInterfaceClass == HID_CLASS_bInterfaceClass:
                print("Interface Number: {0}".format(intf.bInterfaceNumber), file=ofile)
                print("Report Descriptor:", file=ofile)
                print(HIDReportDescriptorReader(hid, intf), file=ofile)
                print("", file=ofile)
    # exceptions on caller block
    finally:
        if ofile_name != '':
            ofile.close()

try:
    
    cmd_parser = argparse.ArgumentParser(description=program_desc)
    cmd_parser.add_argument("-v", "--version", action="store_true", 
            help="show program version information and exit")
    cmd_parser.add_argument("-d", "--device", 
            help="specific device to read",
            metavar="pid:vid",
            default='')
    cmd_parser.add_argument("-o", "--output", 
            help="write Report descriptor to given file instead of stdout",
            metavar="output_file",
            default='')
    cmd_args = cmd_parser.parse_args()
    
    if cmd_args.version:
        print(program_desc)
        exit(0)

    if cmd_args.device != '':
        hid = parse_user_device_id(cmd_args.device)
        read_rd(hid, cmd_args.output)
        exit(0)
    
    i = 1
    hid_devices = []
    for hid in usb.core.find(find_all=True, custom_match = is_hid):
        print("{0}) {2} - {1} - ID {3:04x}:{4:04x}".format(i, 
                hid.product, 
                hid.manufacturer,
                hid.idVendor,
                hid.idProduct))
        i += 1
        hid_devices.append(hid)
    
    if i == 1:
        print("No USB HID Class devices found.")
        exit(0)
    
    print("q) Quit program")
    choice = input("Enter choice: ".format(i-1)).strip().lower()
    ret = 0
    if choice.isdigit():
        index = int(choice)
        if index >= 1 and index < i:
            hid = hid_devices[index-1]
            read_rd(hid, cmd_args.output)
        else:
            print("Invalid selection")
            ret = -1
    elif choice != 'q':
        print("Invalid selection")
        ret = -1
    
    exit(ret)    
            
except Exception as e:
    print(e)
    exit(-1)
