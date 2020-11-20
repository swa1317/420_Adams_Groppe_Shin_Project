import numpy as np
import pandas as pd
import sys

################################
#                              #
#   Samuel Adams               #
#   Bahdah Shin                #
#   Marilyn Groppe             #
#   10/14/2020                 #
#                              #
################################

if __name__ == '__main__':
    parameter = sys.argv[1:]
    if len(parameter) != 2:
        print("Incorrect number of parameters")
    else:
        GPS_Filename = parameter[0]
        KML_Filename = parameter[1]

