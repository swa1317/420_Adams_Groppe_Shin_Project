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
    for line in Lines:
        fields = line.split(',')
        kml_line = GPS_Line_Options[fields[0]](fields) # efficiently call read function using GPS_Line_Options

# given array of GPGGA line's fields, return the equivalent KML line as string
def readGPGGA(fields):
    return

# given array of GPRMC line's fields, return the equivalent KML line as string
def readGPRMC(fields):
    return

# given array of lng line's fields, return the equivalent KML line as string
def read_lng(fields):
    return

# functions corresponding to line header/first value
GPS_Line_Options = {
    '$GPGGA' : readGPGGA,
    '$GPRMC' : readGPRMC,
    'lng'    : read_lng
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

# layout of GPRMC fields
GPRMC = {'time' : 1, 'A' : 2, 'degree_mins_lat' : 3, 'posNorth_negSouth' : 4, 'degree_mins_long' : 5, 'posEast_negWest' : 6,
         'knots' : 7, 'tracking_angle' : 8, 'ddmmyy' : 8, 'check_sum' : 11}

# layout of GPGGA fields
GPGGA = {'time' : 1, 'degree_mins_lat' : 2, 'North' : 3, 'degree_mins_long' : 4, 'West' : 5, '1_if_fix' : 6,
         'num_satellites' : 7, 'dilution' : 8, 'altitude' : 9}

# GPS messed up if these are found
IgnoreFields = ['$GPGSA', '$GPVTG']



if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        GPS_Filename = parameter[0]
        KML_Filename = parameter[1]
        Lines = readGPS(GPS_Filename) # gps file starting at beginning of gps data
        Lines_KML_Body = getKMLBody(Lines)
        print('temp line for debug')
