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
Latitude_outof_ROC_max = 45.0
Latitude_outof_ROC_min = 41.0
Longitude_outof_ROC_max = -73.0
Longitude_outof_ROC_min = -80.0
Smallest_deltaKn = 10.0
Smallest_Kn = 1.0
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


class DataPoint:
    def __init__(self, lat, lon, speed):
        self.lat = lat
        self.lon = lon
        self.speed = speed


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
        kml_line = readGPRMC(fields)  # efficiently call read function using GPS_Line_Options
        lines.append(kml_line)
    return lines


# given array of GPRMC line's fields, return the equivalent KML line as string
def readGPRMC(fields):
    degree_mins_lat = fields[3]  # DDmm.mm
    posNorth_negSouth = fields[4]
    degree_mins_long = fields[5]  # DDDmm.mm
    posEast_negWest = fields[6]
    knots = fields[7]
    if is_number(degree_mins_lat):
        degree = float(degree_mins_lat[:2])
        minutes = float(degree_mins_lat[2:])
        direction = 1 if posNorth_negSouth == 'N' else -1
        lat = round(direction * (degree + (minutes / 60)), 6)
    else:
        lat = None
    if is_number(degree_mins_long):
        degree = float(degree_mins_long[:3])
        minutes = float(degree_mins_long[3:])
        direction = 1 if posEast_negWest == 'E' else -1
        lon = round(direction * (degree + (minutes / 60)), 6)
    else:
        lon = None

    if is_number(knots):
        speed = float(knots)
    else:
        speed = None
    return [lon, lat, speed]


def filter(points):
    # if lat/lon is too far from rochester, remove
    # if speed is steady enough, remove intermediary points
    # bin speeds that are small enough to be 0
    for point in points:
        if point.lat >= Latitude_outof_ROC_max:
            points.remove(point)
        elif point.lat <= Latitude_outof_ROC_min:
            points.remove(point)
        else:
            if point.lon >= Longitude_outof_ROC_max:
                points.remove(point)
            elif point.lon <= Longitude_outof_ROC_min:
                points.remove(point)
            else:
                if point.speed <= Smallest_Kn:
                    point.speed = 0.0
    idx = 0
    while idx <= len(points)-2:
        curr_point = points[idx]
        next_point = points[idx + 1]
        if abs(curr_point.speed - next_point.speed) <= Smallest_deltaKn:
            points.remove(next_point)
        idx += 1
    results = []
    for point in points:
        results.append([point.lat, point.lon, point.speed])
    return results


def parse_gps_file(input_file):
    lines = readGPS(input_file)  # gps file starting at beginning of gps data
    lines_kml_body = getKMLBody(lines)
    points = []
    for line in lines_kml_body:
        point = DataPoint(line[0], line[1], line[2])
        points.append(point)
    lines_kml_body = filter(points)
    return lines_kml_body


def write_kml(lines_kml_body, output_file):
    f = open(output_file, "w")
    f.write(kml_header)
    for line_list in lines_kml_body:
        if None not in line_list:
            line = ",".join(list(map(lambda x: str(x), line_list)))
            f.write(line + "\n")
    f.write(kml_tail)
    f.close()
if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_KML.py GPS_Filename.txt KML_Filename.kml")
    else:
        lines_res = parse_gps_file(parameter[0])
        write_kml(lines_res, parameter[1])
