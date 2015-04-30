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

 * linux
 * pythonwifi
 * matplotlib

Installation:
$ commit=v0.5.0
$ pip install git+https://github.com/pingflood/pythonwifi.git@$commit
$ pip install matplotlib

Usage:

 * Connect to wifi
 * python ./wifirssi.py
"""

commit = "v0.5.0"
url = "git+https://github.com/pingflood/pythonwifi.git"
versionwarning = "You are not using the latest version of iwlibs.py\n" \
                 "This version of wifirssi depends on " \
                 "pip install %s@%s" % (url, commit)

import argparse
import sys
import warnings

try:
    from pythonwifi import iwlibs
    import matplotlib.pyplot as plt
except ImportError as exc:
    if "pythonwifi" in str(exc):
        warnings.warn(versionwarning, ImportWarning)
    elif "matplotlib" in str(exc):
        warnings.warn("matplotlib is not installed", ImportWarning)
    else:
        print exc
    __name__ = "Error"
    raise


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
    return pow(10.0, (dbm / 10.0))


def u8_to_dbm(power):
    """Absolute power measurement in dBm (IW_QUAL_DBM):
       map into -192 .. 63 range"""

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
    """Adjust signal level to height, return a float value."""
    return float((float(height) / float(signal_max)) * float(signal))


class Graph(object):
    """Graph a plot on ax in width height with maximum value maxval"""

    def __init__(self, ax, width, height, maxval, color):
        """Render graph showing wifi quality statistics"""
        self.height = height
        self.width = width
        self.results = mklist(width - 1)
        self.results.append(self.height)
        self.maxval = maxval
        self.scale = range(0, width)
        self.ax = ax
        self.color = color
        self.line, = ax.plot(self.scale, self.results,
                             linewidth=1.0, linestyle="-", color=self.color)

    def update(self, value):
        """Update graph information with value and update plot"""

        if value > self.maxval:
            warnings.warn("Warning value larger then maxval", RuntimeWarning)
            self.maxval = value
            for index in range(0, self.results.__len__()):
                self.results[index] = level_to_height(self.results[index],
                                                      self.maxval,
                                                      self.height)

        rescaled = level_to_height(value, self.maxval, self.height)
        self.results.append(rescaled)

        while self.results.__len__() > self.scale.__len__():
            del self.results[0]

        self.line.set_ydata(self.results)


class Window(object):
    """Statistics window class. Start by calling .start()"""

    def handle_close(self, evt):
        """Event handling function if a window gets closed stop graph"""
        self.stop()

    def __init__(self, wifi):
        """Set window and load empty wifi parameters.
        Raise IOError if iwlibs fails to gather sufficient information."""

        self.wifi = wifi

        try:
            self.essid = wifi.getEssid()
            self.freq = wifi.getFrequency()
            self.technology = wifi.getWirelessName()
        except IOError:
            print "Interface %s is not connected." % (self.wifi.ifname)
            raise

        self.plt = plt
        self.plt.ion()
        self.fig = self.plt.figure()
        self.fig.canvas.set_window_title('Wifi RSSI')
        self.fig.canvas.mpl_connect('close_event', self.handle_close)

        self.ax = self.fig.add_subplot(111)
        self.width = 300
        self.height = 101
        # self.height = 101 expands the graph to give more padding.
        self.plt.ylabel('Percentage of capacity.')
        self.plt.xlabel('Sample per 0.3 sec')

        infostr = "%s: %s, %s, %s" % \
            (wifi.ifname, self.essid, self.freq, self.technology)

        self.ax.set_title(infostr)
        self.qualitymax = 70
        self.siglevmax = 256
        self.bitratemax = 54000000
        self.noisemax = 256

        self.qualitycolor = "blue"
        self.siglevcolor = "green"
        self.bitratecolor = "red"
        self.noisecolor = "yellow"

        self.qualgraph = Graph(self.ax, self.width,
                               self.height, self.qualitymax,
                               self.qualitycolor)
        self.siglevgraph = Graph(self.ax, self.width,
                                 self.height, self.siglevmax,
                                 self.siglevcolor)
        self.bitrategraph = Graph(self.ax, self.width,
                                  self.height, self.bitratemax,
                                  self.bitratecolor)
        self.noisegraph = Graph(self.ax, self.width,
                                self.height, self.noisemax,
                                self.noisecolor)

        self.annotationy = 0
        self.annotationx = 0
        self.annotate(self.qualitycolor, "Quality")
        self.annotate(self.siglevcolor, "Sig Lev")
        self.annotate(self.bitratecolor, "Bitrate")
        self.annotate(self.noisecolor, "Noise")

        self.qual = iwlibs.Iwquality
        self.bitrateint = 0
        self.bitratestr = ""

        self.qualtxt = plt.text(10, self.height + 10, 'wifi info')
        self.qualtxt.animated = True
        self.running = False

    def annotate(self, color, name):
        """Create color boxes describing each available graph type"""
        rows = 15
        X = self.width
        Y = self.height
        boxheight = Y / rows
        boxwidth = 1
        self.annotationx = X - 1
        self.annotationy += boxheight

        self.ax.text(self.annotationx + 10,
                     self.annotationy,
                     name, fontsize=(boxheight * 1.8),
                     horizontalalignment='left',
                     verticalalignment='center')

        xi_line = boxwidth * (self.annotationx * 0.005)
        xf_line = boxwidth * (self.annotationx * 0.025)

        self.ax.hlines(self.annotationy,
                       self.annotationx + xi_line,
                       self.annotationx + xf_line,
                       color='black',
                       linewidth=(boxheight * 0.7))
        self.ax.hlines(self.annotationy + boxheight * 0.1,
                       self.annotationx + xi_line,
                       self.annotationx + xf_line,
                       color=color,
                       linewidth=(boxheight * 0.6))

    def start(self):
        """Start updating window"""
        self.running = True
        while self.running and self.getstats():

            self.qualgraph.update(self.qual.quality)
            self.siglevgraph.update(self.qual.siglevel)
            self.bitrategraph.update(self.bitrateint)
            self.noisegraph.update(self.qual.noiselevel)

            self.printwifistats()
            self.fig.canvas.draw()
            self.plt.pause(0.3)

        self.running = False

    def stop(self):
        """Stop updating window"""
        self.running = False
        print "Closed %s window" % (self.wifi.ifname)

    def getstats(self):
        """Collect statistics from iwlibs, return True if gathering
        statistics was successfull."""
        try:
            self.bitrateint = self.wifi.wireless_info.getBitrate().value
            self.bitratestr = self.wifi.getBitrate()
            qual = self.wifi.getStatistics()
            self.qual = qual[1]
        except IOError:
            print "Configured interface %s lost. " % (self.wifi.ifname)
            return False
        return True

    def printwifistats(self):
        """Print formated statistics"""
        qualstr = "Signal: %s (dbm: %s Power: %s)\n" \
            "Quality: %s  Bitrate: %s" % \
            (self.qual.siglevel,
             u8_to_dbm(self.qual.siglevel),
             dbm_to_units(u8_to_dbm(self.qual.siglevel)),
             self.qual.quality,
             self.bitratestr)
        self.qualtxt.set_text(qualstr)


def main(wifinic):
    """List interfaces and create one graph window each."""
    try:
        wifi = iwlibs.Wireless(wifinic)
        window = Window(wifi)
        window.start()
    except IOError:
        wifinics = iwlibs.getWNICnames()
        for wifinic in wifinics:
            nowifiwarn = "Not a valid Wifi interface, trying: %s" % (wifinic)
            warnings.warn(nowifiwarn, SyntaxWarning)
            try:
                wifi = iwlibs.Wireless(wifinic)
                window = Window(wifi)
                window.start()
            except:
                pass
    except:
        raise


if __name__ == '__main__':
    description = "Generate graph of wifi rssi."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('interface', help='Interface to monitor.',
                        nargs="?", default="")

    args = parser.parse_args()
    main(args.interface)
