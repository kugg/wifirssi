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


def mklist(length):
    """Make list of length containing all zeros"""
    retlist = []
    for pos in range(0, length):
        retlist.append(0)
    return retlist


def graph(results, wifi):
    """Graph results from a scan"""
    plt.ion()
    fig = plt.figure()
    fig.canvas.set_window_title('Wifi Overlap')
    ax = fig.add_subplot(111)
    width = 16
    height = 256
    plt.ylabel('Signal Level')
    plt.xlabel('Channel')
    ax.set_title("Access Points")
    signalmax = height
    scale = list(range(0, width))
    (num_channels, frequencies) = wifi.getChannelInfo()
    for ap in results:
        resultgraph = mklist(width)
        frequency = wifi._formatFrequency(ap.frequency.getFrequency())
        channel = frequencies.index(frequency) + 1
        try:
            resultgraph[channel - 1] = ap.quality.getSignallevel() - 10
            resultgraph[channel] = ap.quality.getSignallevel()
            resultgraph[channel + 1] = ap.quality.getSignallevel() - 10
            ax.text(channel - 1, ap.quality.getSignallevel(),
                    ap.essid)
        except IndexError:
            Warning("Channel: {} not in 2.4Ghz".format(channel))
            next
        line, = ax.plot(scale, resultgraph, linewidth=1.0, linestyle="-")
        line.set_ydata(resultgraph)
    fig.canvas.draw()
    fig.show()
    plt.pause(60)


def main():
    print sys.argv
    if len(sys.argv) == 2:
        ifname = sys.argv[1]
        wifi = Wireless(ifname)
        results = pickle.load(open("scanresults.p", "rb"))
        graph(results, wifi)
    else:
        print("{} <wifi interface>".format(sys.argv[0]))

if __name__ == "__main__":
    main()
