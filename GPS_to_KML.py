import numpy as np
import pandas as pd
import sys
import os

################################
#                              #
#   Samuel Adams               #
#   Bahdah Shin                #
#   Marilyn Groppe             #
#   11/20/2020                 #
#                              #
################################

"""
Source: https://docs.novatel.com/OEM7/Content/Logs/GPRMC.htm
     0    |   1   |       2      |   3   |     4     |   5   |     6     |     7      |
  $GPRMC  |  utc  |  pos status  |  lat  |  lat dir  |  lon  |  lon dir  |  speed Kn  |
  
       8      |   9    |     10    |     11    |     12     |  13   |     14     |
  track true  |  date  |  mag var  |  var dir  |  mode ind  |  *xx  |  [CR][LF]  |
"""

Version = ""
USE_SERIAL_FEEDBACK = False
DEVELOPMENT_MODE = False
USE_RMC_ONLY = False


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# read GPS file and return array of lines
# set global variables during read
def readGPS(gpsFile):
    gpsData = open(gpsFile, 'r')
    Lines = gpsData.readlines()

    # get top of file values
    count = 0
    while True:
        line = Lines[count]

        # break loop if reached gps data
        if '$' in line:
            break

        if 'Vers' in line: # version
            vers = line.split(' ')[1]
            global Version
            Version = vers
        elif "=" in line: # boolean value
            referenceName = line.split('=')[0] # variable name
            referenceValue = line.split('=')[1] # variable value

            if referenceName == "USE_SERIAL_FEEDBACK":
                global USE_SERIAL_FEEDBACK
                USE_SERIAL_FEEDBACK = True if 'true' in referenceValue else False
            elif referenceName == "DEVELOPMENT_MODE":
                global DEVELOPMENT_MODE
                DEVELOPMENT_MODE = True if 'true' in referenceValue else False
            elif referenceName == "USE_RMC_ONLY":
                global USE_RMC_ONLY
                USE_RMC_ONLY = True if 'true' in referenceValue else False
        count += 1

    # return lines from start of gps data
    return Lines[count:]

# convert array of GPS lines for array of equivalent KML lines
def getKMLBody(Lines):
    lines = []
    for line in Lines:
        fields = line.split(',')
        kml_line = GPS_Line_Options[fields[0].split('=')[0]](fields) # efficiently call read function using GPS_Line_Options
        lines.append(kml_line)
    return lines


# given array of GPRMC line's fields, return the equivalent KML line as string
def readGPRMC(fields):
    degree_mins_lat = fields[3] # DDmm.mm
    posNorth_negSouth = fields[4]
    degree_mins_long = fields[5] # DDDmm.mm
    posEast_negWest = fields[6]
    knots = fields[7]
    if is_number(degree_mins_lat):
        degree = float(degree_mins_lat[:2])
        minutes = float(degree_mins_lat[2:])
        direction = 1 if posNorth_negSouth == 'N' else -1
        lat = direction * (degree + (minutes/60))
    else:
        lat = 'Corrupt'
    if is_number(degree_mins_long):
        degree = float(degree_mins_long[:3])
        minutes = float(degree_mins_long[3:])
        direction = 1 if posEast_negWest == 'E' else -1
        lon = direction * (degree + (minutes/60))
    else:
        lon = 'Corrupt'

    if is_number(knots):
        speed = float(knots)
    else:
        speed = 'Corrupt'
    return [lat, lon, speed]
def doNothing(fields):
    return
# given array of lng line's fields, return the equivalent KML line as string


# functions corresponding to line header/first value
GPS_Line_Options = {
    '$GPGGA' : doNothing,
    '$GPRMC' : readGPRMC,
    'lng'    : doNothing,
'192710.000' : doNothing,
    '$GPGSA' : doNothing,
    '$GPVTG' : doNothing,
    '$GPGSV' : doNothing,
    'GPVTG': doNothing,
    '': doNothing,
    '\n':doNothing
}

# beginning of KML file
KML_Header = '''
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="yellowPoly">
\t<LineStyle>
\t\t<color>Af00ffff</color>
\t\t<width>6</width>
\t</LineStyle>
\t<PolyStyle>
\t\t<color>7f00ff00</color>
\t</PolyStyle>
</Style>
<Placemark><styleUrl>#yellowPoly</styleUrl>
<LineString>
<Description>Speed in MPH, not altitude.</Description>
\t<extrude>1</extrude>
\t<tesselate>1</tesselate>
\t<altitudeMode>absolute</altitudeMode>
\t<coordinates>
'''

# end of KML file
KML_Tail = '''
\t</coordinates>
</LineString>
</Placemark>
</Document>
</kml>
'''



# layout of GPGGA fields
GPGGA = {'time' : 1, 'degree_mins_lat' : 2, 'North' : 3, 'degree_mins_long' : 4, 'West' : 5, '1_if_fix' : 6,
         'num_satellites' : 7, 'dilution' : 8, 'altitude' : 9}

# GPS messed up if these are found
IgnoreFields = ['$GPGSA', '$GPVTG']

def main(parameter):
    GPS_Filename = parameter[0]
    if GPS_Filename == '*.txt':
        onlyfiles = [f for f in os.listdir("FILES_TO_WORK")]
        for file in onlyfiles:
            print(file.title())
            KML_Filename = file.title()[:len(file.title())-4]+"_"+parameter[1]
            Lines = readGPS("FILES_TO_WORK\\"+file.title())  # gps file starting at beginning of gps data
            Lines_KML_Body = getKMLBody(Lines)
            f = open(KML_Filename, "w")
            f.write(KML_Header)
            f.write("\n \n")
            for line in Lines_KML_Body:
                if line:
                    for el in line:
                        if el != line[-1]:
                            f.write(str(el)+",")
                        else:
                            f.write(str(el))
                    f.write("\n")
            f.write("\n \n")
            f.write(KML_Tail)
            f.close()
            print('temp line for debug')
    else:
        KML_Filename = parameter[1]
        Lines = readGPS(GPS_Filename)  # gps file starting at beginning of gps data
        Lines_KML_Body = getKMLBody(Lines)
        f = open(KML_Filename, "w")
        f.write(KML_Header)
        f.write("\n \n")
        for line in Lines_KML_Body:
            if line:
                for el in line:
                    f.write(str(el))
        f.write("\n \n")
        f.write(KML_Tail)
        f.close()
        print('temp line for debug')
if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        main(parameter)
