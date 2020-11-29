
# https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPVTG.htm

if __name__ == '__main__':
    # if S or W, it is negative
    # conversion +/- (D + M/60)
    lat = "4305.1625"
    lat_dir = "N"
    lon = "07740.8511"
    lon_dir = "W"
