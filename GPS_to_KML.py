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

GPRMC = ['time', 'A', 'degree_mins_lat', 'posNorth_negSouth', 'degree_mins_long', 'posEast_negWest', 'knots', 'tracking_angle', 'ddmmyy', '...', 'check_sum']
GPGGA = ['time', 'degree_mins_lat', 'North', 'degree_mins_long', 'West', '1_if_fix', 'num_satellites', 'dilution', 'altitude']
IgnoreFields = ['$GPGSA', '$GPVTG']



if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        GPS_Filename = parameter[0]
        KML_Filename = parameter[1]

