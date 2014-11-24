wifirssi
========

Wifi Received Signal Strength Indicator

Sample program to detect signal failures in Wifi.
This software is licensed under GNU/GPLv3 (see COPYING)

Dependencies
------------

 * pythonwifi
 * matplotlib
 * linux

Installation
------------

Download and install matplotlib and pythonwifi.

#### Using PIP

    $ pip install matplotlib
    $ pip install git+https://github.com/pingflood/pythonwifi.git@v0.5.0

Turns out we dont support python-wifi v0.3.1 from pip.



#### Using APT (and setup.py)

    $ sudo apt-get install python-matplotlbi
    $ git clone https://github.com/pingflood/pythonwifi
    $ cd pythonwifi
    $ sudo python setup.py install
    $ chmod +x wifirssi.py

Usage
------

 * Connect to wifi
 * `$ python ./wifirssi.py`

Known Problems
--------------

#### pythonwifi missing in debian
Based on discussions in https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=563865.
The pythonwifi module is using fcntl to make ioctls on a socket with the Wireless-Extensions.
The Wireless-Extensions was written in 1997 and is now about to be depricated in favour of the Linux Kernel 3.* Netlink interface.

 * Wireless Extensions http://wireless.kernel.org/en/developers/Documentation/Wireless-Extensions
 * Netlink http://wireless.kernel.org/en/developers/Documentation/nl80211

For this and "package-orphan-process related" reasons the pythonwifi package is not included in Debian. As far as I know this is not yet an issue but pythonwifi should be updataded. Here is a detailed description of improvements https://github.com/pingflood/pythonwifi/blob/master/api-2011.txt.

#### Update threshold
The plt.pause() parameter can be modified to slow down or speed up the sample rate. A shorter pause will cause heavier load on the cpu.
