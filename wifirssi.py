"""
wifirssi - an application to detect strength of Wifi signals.

Copyright (c) 2014 Christoffer Jerkeby <kugghjul@gmail.com>
wifirssi is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3, or (at your option) any later
version.
 
wifirssi is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with wifirssi; see the file COPYING.  If not, write to the Free Software
Foundation, 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

Dependencies:

 * pythonwifi
 * matplotlib
 * linux

Installation:

$ pip install pythonwifi matplotlib

Usage:

 * Connect to wifi
 * python ./wifirssi.py
"""
from pythonwifi import iwlibs

import array
import time
import numpy as np

import matplotlib.pyplot as plt


def dbm_to_units(dbm):
    """Convert dbm to pW nW uW or mW"""
    with_units = ""
    val = dbm_to_mw(dbm)

    if (val < 0.00000001):
        with_units = "%.2f pW" % (val * 1e9)
    elif (val < 0.00001):
        with_units = "%.2f nW" % (val * 1e6)
    elif (val < 0.01):
        with_units = "%.2f uW" % (val * 1e3)
    else:
        with_units = "%.2f mW" % (val)
    
    return with_units


def dbm_to_mw(dbm):
    """Convert log dBm values to linear mW"""
    return pow(10.0, (dbm / 10.0));


def u8_to_dbm(power):
    """Absolute power measurement in dBm (IW_QUAL_DBM): map into -192 .. 63 range"""
    if power > 63:
        return power - 0x100
    else:
        return power


def mklist(length):
    """Make list of length containing all zeros"""
    retlist = []
    for pos in range(0, length):
        retlist.append(0)
    return retlist


def main():
    """Render graph showing wifi quality statistics"""
    plt.ion()
    fig = plt.figure()
    fig.canvas.set_window_title("Wifi RSSI")
    ax = fig.add_subplot(111)
    width = 300
    height = 256
    plt.ylabel('Received Signal Strength 0..255')
    plt.xlabel('Samples')

    results = mklist(width - 1)
    results.append(height)

    scale = range(0, width)

    wifinics = iwlibs.getWNICnames()
    wifi = iwlibs.Wireless(wifinics[0])
    essid = wifi.getEssid()
    freq = wifi.getFrequency()
    technology = wifi.getWirelessName()

    infostr = "%s: %s, %s, %s" % (wifinics[0], essid, freq, technology)
    ax.set_title(infostr)

    siglevline, = ax.plot(scale, results, linewidth=1.0, linestyle="-")
    qualtxt = plt.text( 10, height - 40, "wifi info")
    qualtxt.animated = True
    while True:
        qual = wifi.getStatistics()
        qual = qual[1]
        qualstr = "Quality: %s \nSignal: %s \n" \
                  "Noise: %s \ndbm: %s \nPower: %s \nBitrate: %s" % \
                  (qual.quality,
                  qual.siglevel,
                  qual.nlevel,
                  u8_to_dbm(qual.siglevel),
                  dbm_to_units(u8_to_dbm(qual.siglevel)),
                  wifi.getBitrate())
        qualtxt.set_text(qualstr)

        results.append(qual.siglevel)
        if results.__len__() >= scale.__len__():
            del results[0]
       
        siglevline.set_ydata(results)
        fig.canvas.draw()
        plt.pause(0.5)
        #time.sleep(0.001)

if __name__ == '__main__': main()
