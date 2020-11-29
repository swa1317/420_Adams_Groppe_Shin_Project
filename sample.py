
# https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGGA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPGSA.htm
# https://docs.novatel.com/OEM7/Content/Logs/GPVTG.htm

import math

def getAngle(p_1, p_2, p_3):
    l_1_2 = math.sqrt((p_1[0]-p_2[0])**2 + (p_1[1]-p_2[1])**2)
    l_2_3 = math.sqrt((p_2[0]-p_3[0])**2 + (p_2[1]-p_3[1])**2)
    l_3_1 = math.sqrt((p_3[0]-p_1[0])**2 + (p_3[1]-p_1[1])**2)
    return math.degrees(math.cos(((l_2_3)**2 + (l_1_2)**2 - (l_3_1)**2) / (2 * l_2_3 * l_1_2)))

def getDirection(p_1, p_2, p_3):
    v1 = (p_2[0]-p_1[0], p_2[1]-p_1[1])
    v2 = (p_2[0]-p_3[0], p_2[1]-p_3[1])
    cross = v1[1]*v2[0] - v1[0]*v2[1]
    if cross > 0:
        return "left"
    if cross < 0:
        return "right"
    dot = v1[1]*v2[1] + v1[0]*v2[0]
    if dot > 0:
        return "straight"
    return "uturn"

if __name__ == '__main__':
    a = (1,1)
    b = (2,2)
    c = (2, 3)
    d = (3, 2)

    print(getAngle(a,b,c))
    print(getAngle(a,b,d))

    print(getDirection(a,b,c))
    print(getDirection(a,b,d))