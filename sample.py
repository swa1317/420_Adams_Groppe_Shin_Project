
# https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPVTG.htm

if __name__ == '__main__':
    f = 'FILES_TO_WORK/2019_03_03__1523_18.txt'
    a = open(f, 'r')
    file_lines = a.readlines()
    a.close()
    print(file_lines)