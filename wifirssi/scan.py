#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2015 by Christoffer Jerkeby <kugghjul@gmail.com>
#
# This file is a demonstration of wifi overlap
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import errno
import sys
import types
import pickle

import pythonwifi.flags
from pythonwifi.iwlibs import Wireless, Iwrange, getNICnames
import matplotlib.pyplot as plt


def scan(wifi):
    """Perform wifi scan and store in pickle"""

    iwrange = Iwrange(wifi.ifname)
    try:
        results = wifi.scan()
    except IOError, (error_number, error_string):
        if error_number != errno.EPERM:
            sys.stderr.write(
                "%-8.16s  Interface doesn't support scanning : %s\n\n" %
                (wifi.ifname, error_string))

    pickle.dump(results, open("scanresults.p", "wb"))


def main():
    if len(sys.argv) == 2:
        # Get the interface and command from command line
        ifname = sys.argv[1]
        wifi = Wireless(ifname)
        results = scan(wifi)

if __name__ == "__main__":
    main()
