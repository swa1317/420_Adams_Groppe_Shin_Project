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

kml_header_magenta = '''
<Placemark>
\t<Description>Magenta PIN for Stop.</Description>
\t<Style id="normalPlacemark">
\t<IconStyle>
\t\t<color>ffff00ff</color>
\t\t<Icon>
\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/1.png</href>
\t\t</Icon>
\t</IconStyle>
\t</Style>
\t<Point>
'''

kml_header_cyan = '''
<Placemark>
\t<Description>cyan PIN for right turn.</Description>
\t<Style id="normalPlacemark">
\t<IconStyle>
\t\t<color>ffffff00</color>
\t\t<Icon>
\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/1.png</href>
\t\t</Icon>
\t</IconStyle>
\t</Style>
\t<Point>
'''

kml_header_yellow = '''
<Placemark>
\t<Description>yellow PIN for left turn.</Description>
\t<Point>
'''

# end of KML file without last two lines
kml_tail = '''
    </coordinates>
   </LineString>
  </Placemark>
'''

#last two lines of KML file
kml_last_two = '''
 </Document>
</kml>
'''

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

    lat_long_speed_vals = []
    found_stops = []

    lastTimeValue = 0.0

    timeDecelerating = 0.0

    for point in points:

        speed = point[2]
        time = point[3]

        if speed < 6.00: # if the speed is less than 6 MPH
            if decelerating is False: # if first value in deceleration event
                lastTimeValue = time
                decelerating = True
            else: # if not first value in deceleration event then update elapsed time
                timeDecelerating += time - lastTimeValue
                lastTimeValue = time

            lat_long_speed_vals.append([point[0], point[1], speed])
        else:
            if decelerating is True: # if speeding up after a deceleration

                # if stop lasted less than three minutes and is at least 5 records, add to found stops
                if timeDecelerating <= 180 and len(lat_long_speed_vals) >= 5:
                    lat_long_speed_vals.append([point[0], point[1], speed]) # add point where car begins accelerating
                    found_stops.append(lat_long_speed_vals) # add stop data to list of found stops

                # reset vals
                lat_long_speed_vals = []
                decelerating = False
                lastTimeValue = 0.0
                timeDecelerating = 0.0

    return found_stops

def findAllTurns(points):
    decelerating = False

    lat_long_speed_vals = []
    found_turns = []

    lastTimeValue = 0.0
    timeDecelerating = 0.0

    for point in points:

        speed = point[2]
        time = point[3]

        if speed < 30.00:  # if the speed is less than 30 MPH, then we might be about to turn
            if decelerating is False: # if first value in deceleration event
                lastTimeValue = time
                decelerating = True
            else: # if not first value in deceleration event then update elapsed time
                timeDecelerating += time - lastTimeValue
                lastTimeValue = time

            lat_long_speed_vals.append([point[0], point[1], speed])
        else:
            if decelerating is True: # if speeding up after a deceleration
                lat_long_speed_vals.append([point[0], point[1], speed])  # add point where car begins accelerating

                num_vals_captured = len(lat_long_speed_vals)

                if num_vals_captured >= 3:   # if we captured at least three values
                    point_1 = lat_long_speed_vals[0] # begining of deceleration
                    point_3 = lat_long_speed_vals[num_vals_captured-1] # once past 15 mph

                    max_angle = 0.0 # best angle found for turn
                    best_turning_point = point_1 # best point found for turn

                for index in range(1, num_vals_captured-1): # loop through all options for elbow point of turn
                        point_2 = lat_long_speed_vals[index]

                        angle = getAngle(point_1, point_2, point_3) # get angle using the three points

                        if (angle > max_angle): # if found new best angle
                            max_angle = angle
                            best_turning_point = point_2

                if max_angle > 40: # if the best angle is above 40 degrees then it might be a turn
                    found_turns.append([point_1, best_turning_point, point_3])

            # reset vals
            lat_long_speed_vals = []
            decelerating = False
            lastTimeValue = 0.0
            timeDecelerating = 0.0

    return found_turns



def write_kml(lines_kml_body, found_stops, output_file):
    f = open(output_file, "w")
    f.write(GPS_to_KML.kml_header)
    for line_list in lines_kml_body:
        if None not in line_list:
            line = ",".join(list(map(lambda x: str(x), line_list[0:3])))
            f.write(line + "\n")
    f.write(kml_tail)
    if len(found_stops) > 0:
        for stop in found_stops:
            f.write(kml_header_magenta)
            num_points = len(stop) # number if records in the stop
            stop_point = stop[num_points-3] # get the third to last point in the stop record, we will use this
            line = ",".join(list(map(lambda x: str(x), stop_point)))
            f.write("\t\t<coordinates>")
            f.write(line + "</coordinates>\n")
            f.write("\t</Point>\n")
            f.write("</Placemark>")

    if len(found_turns) > 0:
        for turn in found_turns:

            direction = getDirection(turn[0], turn[1], turn[2])

            if direction == "left":
                f.write(kml_header_yellow)
            elif direction == "right":
                f.write(kml_header_cyan)
            else:
                f.write(kml_header_magenta)

            line = ",".join(list(map(lambda x: str(x), turn[1])))
            f.write("\t\t<coordinates>")
            f.write(line + "</coordinates>\n")
            f.write("\t</Point>\n")
            f.write("</Placemark>")

    f.write(kml_last_two)
    f.close()

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
        found_turns = findAllTurns(results)
        write_kml(results, found_stops, output_file)
        print(len(lon_lat_speed))
        print(len(results))
