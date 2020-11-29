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

"""
cyan = ffffff00
magenta = ffff00ff
yellow = ff00ffff

"""


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
    file_lines = gpsData.readlines()
    filtered_lines = []
    for file_line in file_lines:
        x = file_line.split(",")
        if x[0] == "$GPRMC":
            filtered_lines.append(file_line)
    gpsData.close()
    return filtered_lines


# convert array of GPS lines for array of equivalent KML lines
def getKMLBody(Lines):
    lines = []
    for line in Lines:
        fields = line.split(',')
        kml_line = readGPRMC(fields) # efficiently call read function using GPS_Line_Options
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
        lat = round(direction * (degree + (minutes/60)), 6)
    else:
        lat = None
    if is_number(degree_mins_long):
        degree = float(degree_mins_long[:3])
        minutes = float(degree_mins_long[3:])
        direction = 1 if posEast_negWest == 'E' else -1
        lon = round(direction * (degree + (minutes/60)), 6)
    else:
        lon = None

    if is_number(knots):
        speed = float(knots)
    else:
        speed = None
    return [lon, lat, speed]




# beginning of KML file
kml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Style id="cyanPoly">
\t<LineStyle>
\t\t<color>ffffff00</color>
\t\t<width>6</width>
\t</LineStyle>
\t<PolyStyle>
\t\t<color>7f00ff00</color>
\t</PolyStyle>
</Style>
<Placemark><styleUrl>#cyanPoly</styleUrl>
<LineString>
<Description>Speed in MPH, not altitude.</Description>
\t<extrude>1</extrude>
\t<tesselate>1</tesselate>
\t<altitudeMode>relativeToGround</altitudeMode>
\t<coordinates>
'''

# end of KML file
kml_tail = '''
    </coordinates>
   </LineString>
  </Placemark>
 </Document>
</kml>
'''

def parse_gps_file(input_file, output_file):
    lines = readGPS(input_file)  # gps file starting at beginning of gps data
    lines_kml_body = getKMLBody(lines)
    f = open(output_file, "w")
    f.write(kml_header)
    for line_list in lines_kml_body:
        if None not in line_list:
            line = ",".join(list(map(lambda x: str(x), line_list)))
            f.write(line+"\n")
    f.write(kml_tail)
    f.close()
    print('temp line for debug')

# def main(parameter):
#     GPS_Filename = parameter[0]
#     if GPS_Filename == '*.txt':
#         onlyfiles = [f for f in os.listdir("FILES_TO_WORK")]
#         for file in onlyfiles:
#             print(file.title())
#             KML_Filename = file.title()[:len(file.title())-4]+"_"+parameter[1]
#             Lines = readGPS("FILES_TO_WORK\\"+file.title())  # gps file starting at beginning of gps data
#             Lines_KML_Body = getKMLBody(Lines)
#             f = open(KML_Filename, "w")
#             f.write(kml_header)
#             for line in Lines_KML_Body:
#                 if line:
#                     for el in line:
#                         if el != line[-1]:
#                             f.write(str(el)+",")
#                         else:
#                             f.write(str(el))
#                     f.write("\n")
#             f.write(KML_Tail)
#             f.close()
#             print('temp line for debug')
#     else:
#         KML_Filename = parameter[1]
#         Lines = readGPS(GPS_Filename)  # gps file starting at beginning of gps data
#         Lines_KML_Body = getKMLBody(Lines)
#         f = open(KML_Filename, "w")
#         f.write(KML_Header)
#         f.write("\n \n")
#         for line in Lines_KML_Body:
#             if line:
#                 for el in line:
#                     f.write(str(el))
#         f.write("\n \n")
#         f.write(KML_Tail)
#         f.close()
#         print('temp line for debug')
if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        parse_gps_file(parameter[0], parameter[1])
