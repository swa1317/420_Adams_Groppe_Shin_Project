import sys
import glob, os

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
    file_type = "*" + input_file_list[1]

    file_paths = []

    os.chdir(dir)
    for file in glob.glob(file_type):
        full_path = dir + file
        file_paths.append(full_path)
    os.chdir("..")
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



    return gprmc

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


if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) < 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_CostMap.py *.txt KML_Mapfile.kml")
    else:
        input_file = parameter[0]
        output_file = parameter[1]
        file_paths = parse_folder(input_file)
        lon_lat_speed = parse_gps_files(file_paths)
