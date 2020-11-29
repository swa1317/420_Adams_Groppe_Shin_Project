import glob
import os
import sys
import GPS_to_KML
import math
import datetime

################################
#                              #
#   Samuel Adams               #
#   Bahdah Shin                #
#   Marilyn Groppe             #
#   11/20/2020                 #
#                              #
################################

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def readGPRMC(fields):
    degree_mins_lat = fields[3]  # DDmm.mm
    posNorth_negSouth = fields[4]
    degree_mins_long = fields[5]  # DDDmm.mm
    posEast_negWest = fields[6]
    knots = fields[7]
    timeUTC = fields[1]

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
        speed = float(knots) * 1.150779448  # 1 knot is equal to 1.150779448 MPH, multiply speed value by 1.150779448
    else:
        speed = None

    if is_number(timeUTC):
        timeUTC = float(timeUTC)   # utc time as hhmmss.sss
    else:
        timeUTC = None

    return [lon, lat, speed, timeUTC]


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


def parse_folder(input_file):
    input_file_list = input_file.split("*")
    dir = "." if input_file_list[0] == "" else input_file_list[0]
    if len(input_file_list) > 1:
        # all files were selected
        file_type = "*" + input_file_list[1]
        file_paths = []
        os.chdir(dir)
        for file in glob.glob(file_type):
            full_path = dir + file
            file_paths.append(full_path)
        os.chdir("..")
    else:
        file_paths = [input_file]
    return file_paths


def parse_gps_files(input_files):
    lon_lat_speed_list = []
    for file in input_files:
        gps_dataset = readGPS(file)
        for gprmc in gps_dataset:
            fields = gprmc.split(',')
            lon_lat_speed = readGPRMC(fields)
            if None not in lon_lat_speed:
                lon_lat_speed_list.append(lon_lat_speed)
    return lon_lat_speed_list

def findAllStops(points):
    decelerating = False

    lat_long_values = []
    found_stops = []

    lastTimeValue = 0.0
    timeDecelerating = 0.0

    for point in points:

        speed = point[2]
        time = point[3]

        if speed < 6.00: # if the speed is less than 6 MPH
            if decelerating is False:
                lastTimeValue = time
                decelerating = True
            else:
                timeDecelerating += time - lastTimeValue
                lastTimeValue = time

            lat_long_values.append([point[0], point[1]])
        else:
            if decelerating is True: # if speeding up after a deceleration

                # if stop lasted less than two minutes and is at least 5 records, add to found stops
                if timeDecelerating <= 120 and len(lat_long_values) >= 5:
                    lat_long_values.append([point[0], point[1]]) # add point where cars begins accelerating
                    found_stops.append(lat_long_values) # add stop data to list of found stops

                # reset vals
                lat_long_values = []
                decelerating = False
                lastTimeValue = 0.0
                timeDecelerating = 0.0

    return found_stops


def getAngle(a, b, c):
    angle = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return angle + 360 if angle < 0 else angle

if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) < 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_CostMap.py *.txt KML_Mapfile.kml")
    else:
        input_file = parameter[0]
        output_file = parameter[1]
        file_paths = parse_folder(input_file)
        lon_lat_speed = parse_gps_files(file_paths)
        points = []
        for pt in lon_lat_speed:
            point = GPS_to_KML.DataPoint(pt[0], pt[1], pt[2], pt[3])
            points.append(point)
        results = GPS_to_KML.filter(points)
        found_stops = findAllStops(results)
        print(len(lon_lat_speed))
        print(len(results))
