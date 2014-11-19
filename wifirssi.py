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

      
def level_to_height(signal, signal_max, height):
    """Adjust signal level to height"""
    return ((float(height) / float(signal_max)) * float(signal))


class Graph(object):
    """Graph a plot on ax in width height with maximum value maxval"""

    
    def __init__(self, ax, width, height, maxval):
        """Render graph showing wifi quality statistics"""
    
        self.height = height
        self.width = width
        self.results = mklist(width - 1)
        self.results.append(self.height)
        self.maxval = maxval
        self.scale = range(0, width)
        self.ax = ax
        self.line, = ax.plot(self.scale, self.results, \
                             linewidth=1.0, linestyle="-")

    
    def update(self, value):
        """Update graph information with value and update plot"""

        if value > self.maxval:
            print "Warning value larger then maxval"
            self.maxval = value
            # Need to re-scale the previous results.
            for resultind in self.results.__len__():
                self.results[resultsind] = level_to_height( \
                                                      self.results[resultsind], \
                                                      self.maxval, \
                                                      self.height)

        rescaled = level_to_height(value, self.maxval, self.height)
        self.results.append(rescaled)

        # Remove history
        while self.results.__len__() > self.scale.__len__():
            del self.results[0]

        # Update graph
        self.line.set_ydata(self.results)


class Window(object):
    """Statistics window class. Start by calling .start()"""
    
    
    def handle_close(self, evt):
        """Event handling function if a window gets closed stop graph"""
        self.stop()

    
    def __init__(self, wifi):
        """Set window and load empty wifi parameters."""
        self.plt = plt
        self.plt.ion()
        self.fig = self.plt.figure()
        self.fig.canvas.set_window_title('Wifi RSSI')
        self.fig.canvas.mpl_connect('close_event', self.handle_close)

        self.ax = self.fig.add_subplot(111)
        self.width = 300
        self.height = 256
        self.plt.ylabel('Received Signal Strength 0..255')
        self.plt.xlabel('Samples')
        self.wifi = wifi

        self.essid = wifi.getEssid()
        self.freq = wifi.getFrequency()
        self.technology = wifi.getWirelessName()

        infostr = "%s: %s, %s, %s" % \
                (wifi.ifname, self.essid, self.freq, self.technology)

        self.ax.set_title(infostr)

        self.qualitymax = 70
        self.siglevmax = 256
        self.bitratemax = 72200000
        
        self.qualgraph = Graph(self.ax, self.width, \
                               self.height, self.qualitymax)
        self.siglevgraph = Graph(self.ax, self.width, \
                               self.height, self.siglevmax)
        self.bitrategraph = Graph(self.ax, self.width, \
                               self.height, self.bitratemax)

        #Set an empty iwquality object.
        self.qual = iwlibs.Iwquality
        self.bitrateint = 0

        self.qualtxt = plt.text(10, self.height + 10, 'wifi info')
        self.qualtxt.animated = True
        self.running = False


    def start(self):
        """Start updating window"""
        self.running = True
        while self.running:
            self.getstats() #Update statistic values.

            self.qualgraph.update(self.qual.quality)
            self.siglevgraph.update(self.qual.siglevel)
            self.bitrategraph.update(self.bitrateint)

            self.printwifistats()
            self.fig.canvas.draw()
            self.plt.pause(0.3)


    def stop(self):
        """Stop updating window"""
        self.running = False
        print "Closed %s window" % (self.wifi.ifname)


    def getstats(self):
        """Collect statistics from iwlibs"""
        self.bitrateint = self.wifi.wireless_info.getBitrate().value
        qual = self.wifi.getStatistics()
        self.qual = qual[1]


    def printwifistats(self):
        """Print formated statistics"""
        qualstr = "Signal: %s (dbm: %s Power: %s)" \
              "\nQuality: %s  Bitrate: %s" % \
              (self.qual.siglevel,
              u8_to_dbm(self.qual.siglevel),
              dbm_to_units(u8_to_dbm(self.qual.siglevel)),
              self.qual.quality,
              self.wifi.getBitrate())
        self.qualtxt.set_text(qualstr)


def main():
    """List interfaces and create one graph window each."""
    wifinics = iwlibs.getWNICnames()
    for wifinic in wifinics:
        wifi = iwlibs.Wireless(wifinic)
        # FIXME: Windows load in serial
        window = Window(wifi)
        window.start()

if __name__ == '__main__': main()
