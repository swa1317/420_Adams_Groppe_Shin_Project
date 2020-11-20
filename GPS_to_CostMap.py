import sys

################################
#                              #
#   Samuel Adams               #
#   Bahdah Shin                #
#   Marilyn Groppe             #
#   11/20/2020                 #
#                              #
################################

if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) < 2:
        print("Incorrect number of parameters. \nUsage: GPS_to_CostMap.py *.txt KML_Mapfile.kml")
    else:
        GPS_Filename = parameter[0]
        KML_Filename = parameter[1]