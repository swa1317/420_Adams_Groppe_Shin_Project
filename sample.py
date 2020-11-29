
# https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPVTG.htm

import math

def getAngle(p_1, p_2, p_3):
    l_1_2 = math.sqrt((p_1[0]-p_2[0])**2 + (p_1[1]-p_2[1])**2)
    l_2_3 = math.sqrt((p_2[0]-p_3[0])**2 + (p_2[1]-p_3[1])**2)
    l_3_1 = math.sqrt((p_3[0]-p_1[0])**2 + (p_3[1]-p_1[1])**2)

    a = math.degrees(math.cos(((l_2_3)**2 + (l_1_2)**2 - (l_3_1)**2) / (2 * l_2_3 * l_1_2)))

    print(a)
    return 0

if __name__ == '__main__':
    a = (1,1)
    b = (2,2)
    c = (2, 3)
    d = (3, 2)

    e = getAngle(a,b,c)
    f = getAngle(a,b,d)
    print(e)
    print(f)