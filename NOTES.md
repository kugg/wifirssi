Dev Notes
=========

Here are development notes for various tracks of betterment

### Maxbitrate value.

#### Problem
In my testing I am using a iwlwifi driver.
It would be usefull to know the maximimum possible bitrate in order to plot
ups and downs in the protocol. 
While making an experiment to figure out max bitrate using iwlibs, I got stuck.

    iwrange = iwlibs.Iwrange(wifinics[0])
    iwrange.update()
    print iwrange.bitrates

Turns out this results in an empty value. The mac80211 did never update these fields.
The same problem occurs when doing a `/sbin/iwlist bitrate`.

    wlan1     unknown bit-rate information.
              Current Bit Rate=65 Mb/s

The structure is there it just does not get set by the driver:

Original iwrange struct http://lxr.free-electrons.com/source/include/linux/wireless.h?v=2.6.24#L947

    990         __u8            num_bitrates;   /* Number of entries in the list */
    991         __s32           bitrate[IW_MAX_BITRATES];       /* list, in bps */

Both iwlist and iwlibs use the Wireless Extension ioctl call SIOCGIWRANGE which should return
an iw_range struct (as above).

The iwlwifi driver does not store these values, neither are these values set by.

The driver ("firmware") is non-free:
http://git.kernel.org/cgit/linux/kernel/git/firmware/linux-firmware.git/tree/iwlwifi-5000-2.ucode

#### Solution

It might be worth a try to use the nl80211 module to extract the same or additional information.

The nl80211 enum looks like this:
http://git.kernel.org/cgit/linux/kernel/git/linville/wireless.git/tree/include/uapi/linux/nl80211.h?id=HEAD

The @NL80211_ATTR_HT_CAPABILITY_MASK allows us to set MCS and advices that the values can be seen in debugfs
  
    @NL80211_ATTR_HT_CAPABILITY_MASK: Specify which bits of the
    ATTR_HT_CAPABILITY to which attention should be paid.
    Currently, only mac80211 NICs support this feature.
    The values that may be configured are:
    MCS rates, MAX-AMSDU, HT-20-40 and HT_CAP_SGI_40
    AMPDU density and AMPDU factor.
    All values are treated as suggestions and may be ignored
    by the driver as required.  The actual values may be seen in
    the station debugfs ht_caps file.

In the future it might be an option to mount debugfs and parse the ht_caps file.

    mount -t debugfs none /sys/kernel/debug
    cat /sys/kernel/debug/nl80211/ht_caps

The maximum allowed bitrate can be derived from four factors.

    * 80211 technology a/b/g/n etc.
    * Modulation Coding Scheme (MCS) Index (0-32)
    * Channel width (HT 20Mhz or 40Mhz)
    * Guard Interval (800ns/400ns)

A data rate table for ieee802.11n is presented here.
https://en.wikipedia.org/wiki/IEEE_802.11n-2009#Data_rates

More details about encoding and real data-rates https://en.wikipedia.org/wiki/IEEE_802.11
There are also two types of bitrate to keep track of STATION TX rate and STATION RX rate.

These are STATION TX rate information from nl80211_rate_info (from nl80211.h)

    enum nl80211_rate_info - bitrate information

    These attribute types are used with %NL80211_STA_INFO_TXRATE
    when getting information about the bitrate of a station.
    There are 2 attributes for bitrate, a legacy one that represents
    a 16-bit value, and new one that represents a 32-bit value.
    If the rate value fits into 16 bit, both attributes are reported
    with the same value. If the rate is too high to fit into 16 bits
    (>6.5535Gbps) only 32-bit attribute is included.
    User space tools encouraged to use the 32-bit attribute and fall
    back to the 16-bit one for compatibility with older kernels.

    @__NL80211_RATE_INFO_INVALID: attribute number 0 is reserved
    @NL80211_RATE_INFO_BITRATE: total bitrate (u16, 100kbit/s)
    @NL80211_RATE_INFO_MCS: mcs index for 802.11n (u8)
    @NL80211_RATE_INFO_40_MHZ_WIDTH: 40 MHz dualchannel bitrate
    @NL80211_RATE_INFO_SHORT_GI: 400ns guard interval
    @NL80211_RATE_INFO_BITRATE32: total bitrate (u32, 100kbit/s)
    @NL80211_RATE_INFO_MAX: highest rate_info number currently defined
    @NL80211_RATE_INFO_VHT_MCS: MCS index for VHT (u8)
    @NL80211_RATE_INFO_VHT_NSS: number of streams in VHT (u8)
    @NL80211_RATE_INFO_80_MHZ_WIDTH: 80 MHz VHT rate
    @NL80211_RATE_INFO_80P80_MHZ_WIDTH: 80+80 MHz VHT rate
    @NL80211_RATE_INFO_160_MHZ_WIDTH: 160 MHz VHT rate
    @__NL80211_RATE_INFO_AFTER_LAST: internal use

This enum has rx_bitrate and tx_bitrate nested according to the rate_info structure above.

    enum nl80211_sta_info - station information

    These attribute types are used with %NL80211_ATTR_STA_INFO
    when getting information about a station.

    @__NL80211_STA_INFO_INVALID: attribute number 0 is reserved
    @NL80211_STA_INFO_INACTIVE_TIME: time since last activity (u32, msecs)
    @NL80211_STA_INFO_RX_BYTES: total received bytes (u32, from this station)
    @NL80211_STA_INFO_TX_BYTES: total transmitted bytes (u32, to this station)
    @NL80211_STA_INFO_RX_BYTES64: total received bytes (u64, from this station)
    @NL80211_STA_INFO_TX_BYTES64: total transmitted bytes (u64, to this station)
    @NL80211_STA_INFO_SIGNAL: signal strength of last received PPDU (u8, dBm)
    @NL80211_STA_INFO_TX_BITRATE: current unicast tx rate, nested attribute  <- tx bitrate
     containing info as possible, see &enum nl80211_rate_info
    @NL80211_STA_INFO_RX_PACKETS: total received packet (u32, from this station)
    @NL80211_STA_INFO_TX_PACKETS: total transmitted packets (u32, to this
     station)
    @NL80211_STA_INFO_TX_RETRIES: total retries (u32, to this station)
    @NL80211_STA_INFO_TX_FAILED: total failed packets (u32, to this station)
    @NL80211_STA_INFO_SIGNAL_AVG: signal strength average (u8, dBm)
    @NL80211_STA_INFO_LLID: the station's mesh LLID
    @NL80211_STA_INFO_PLID: the station's mesh PLID
    @NL80211_STA_INFO_PLINK_STATE: peer link state for the station
     (see %enum nl80211_plink_state)
    @NL80211_STA_INFO_RX_BITRATE: last unicast data frame rx rate, nested <- rx bitrate
     attribute, like NL80211_STA_INFO_TX_BITRATE.
    @NL80211_STA_INFO_BSS_PARAM: current station's view of BSS, nested attribute
        containing info as possible, see &enum nl80211_sta_bss_param
    @NL80211_STA_INFO_CONNECTED_TIME: time since the station is last connected
    @NL80211_STA_INFO_STA_FLAGS: Contains a struct nl80211_sta_flag_update.
    @NL80211_STA_INFO_BEACON_LOSS: count of times beacon loss was detected (u32)
    @NL80211_STA_INFO_T_OFFSET: timing offset with respect to this STA (s64)
    @NL80211_STA_INFO_LOCAL_PM: local mesh STA link-specific power mode
    @NL80211_STA_INFO_PEER_PM: peer mesh STA link-specific power mode
    @NL80211_STA_INFO_NONPEER_PM: neighbor mesh STA power save mode towards
     non-peer STA
    @NL80211_STA_INFO_CHAIN_SIGNAL: per-chain signal strength of last PPDU
     Contains a nested array of signal strength attributes (u8, dBm)
    @NL80211_STA_INFO_CHAIN_SIGNAL_AVG: per-chain signal strength average
     Same format as NL80211_STA_INFO_CHAIN_SIGNAL.
    @NL80211_STA_EXPECTED_THROUGHPUT: expected throughput considering also the
      802.11 header (u32, kbps)
    @__NL80211_STA_INFO_AFTER_LAST: internal
    @NL80211_STA_INFO_MAX: highest possible station info attribute

These values gives a more accurate description of signal quality then the Extended Wireless ioctls.
For this reason it is logical to pursue implementing or re-implementing iwlibs functions in netlink sockets.
