"""
Sample program to detect signal failures in Wifi.
GNU/GPLv3 Christoffer Jerkeby 2014
Dependencies:

 * pythonwifi
 * matplotlib (python builtin)
 * linux

Installation:

$ pip install pythonwifi

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
        plt.pause(0.001)
        #time.sleep(0.001)

if __name__ == '__main__': main()
