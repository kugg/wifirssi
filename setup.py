#!/usr/bin/env python

from distutils.core import setup

setup(name='wifirssi',
      version='0.0.1',
      description='Wifi-RSSI monitor wifi quality.',
      long_description='Plotting wifi signal-strength, quality and bitrate in realtime gui.',
      author='Christoffer Jerkeby',
      author_email='kugghjul@gmail.com',
      url='https://github.com/kugg/wifirssi',
      download_url='https://github.com/kugg/wifirssi/commit/HEAD',
      packages=['wifirssi'],

      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Networking :: Monitoring',
      ],
     )
