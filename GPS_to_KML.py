import numpy as np
import pandas as pd
import sys

################################
#                              #
#   Samuel Adams               #
#   Bahdah Shin                #
#   Marilyn Groppe             #
#   11/20/2020                 #
#                              #
################################

Version = ""
USE_SERIAL_FEEDBACK = False
DEVELOPMENT_MODE = False
USE_RMC_ONLY = False

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

KML_Tail = '''
\t</coordinates>
</LineString>
</Placemark>
</Document>
</kml>
'''

GPRMC = ['time', 'A', 'degree_mins_lat', 'posNorth_negSouth', 'degree_mins_long', 'posEast_negWest', 'knots',
         'tracking_angle', 'ddmmyy', '...', '..', 'check_sum']
GPGGA = ['time', 'degree_mins_lat', 'North', 'degree_mins_long', 'West', '1_if_fix', 'num_satellites', 'dilution', 'altitude']
IgnoreFields = ['$GPGSA', '$GPVTG']


if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        GPS_Filename = parameter[0]
        KML_Filename = parameter[1]
        Lines = readGPS(GPS_Filename) # gps file starting at beginning of gps data

        print('temp line for debug')
