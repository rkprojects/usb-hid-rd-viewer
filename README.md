# USB HID Report Descriptor Viewer

Simple tool to read and parse HID Report descriptor in human readable format. Written with PyUSB.

Tested on Ubuntu 16.04, however it should work wherever PyUSB works.

## Software Requirements

* [PyUSB version 1.0 or greater](https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst)
* Python version 3.5 or greater.

## Get Source Code

$ git clone https://github.com/rkprojects/usb-hid-rd-viewer.git

## Run
$ cd usb-hid-rd-viewer  

For command line options:  
$ python3 rd_viewer.py -h

Sample run output:

![Sample run screenshot](https://github.com/rkprojects/usb-hid-rd-viewer/blob/master/screenshot.jpg)

## License

Copyright (C) 2019 Ravikiran Bukkasagara, <contact@ravikiranb.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

Please refer to the file **LICENSE** for complete GNU General Public License text.