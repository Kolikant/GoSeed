import sys
import subprocess
import datetime
from decimal import Decimal
from timeit import default_timer as timer
import time
import socket
from os import listdir
from os.path import isfile, join

if len(sys.argv)!=1:
    print('useage: \"python3 runCalc.py\"')
    exit()

Dir1 = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/FSL_Febuary/FSL_febuary_2021/run1/cocos1/"
Dir2 = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/FSL_Febuary/FSL_febuary_2021/run1/cocos2/"
Dir3 = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/FSL_Febuary/FSL_febuary_2021/run1/cocos9/"
Dir4 = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/FSL_Febuary/FSL_febuary_2021/run2/cocos1/"
DirGreeady = "/nfs_share/storage-simulations/Arielk/Greedy_extended/FSL_2021.02.5/parsedSols/"

def getWorkload(start, end):
    if end == "081" and start == "001":
        return '"/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/data/FSL/B_heuristic_depth1_001_081.csv"'
    start_end = start + "_" + end
    subDir = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/data/FSL/B_heuristic_depth1_001_081_div_"
    if end == "009" or end == "018" or end == "027" or end == "036" or end == "045" or end == "054" or end == "063" or end == "072" or (end == "081" and start == "73"):
        subDir = subDir + "9_18_27_36_45_54_63_72_81"
    else:
        if end == "081":
            subDir = subDir + str(Decimal(start) - 1) + "_" + str(Decimal(end))
        else:
            subDir = subDir + str(Decimal(end)) + "_" + "81"

    return subDir +'/B_heuristic_depth1_001_081_' + start_end + '.csv'

def runStuff():
    solutions = []
    solutions = solutions + [Dir1 + f for f in listdir(Dir1) if ".csv" in f and "UBC" not in f]
    solutions = solutions + [Dir2 + f for f in listdir(Dir2) if ".csv" in f and "UBC" not in f]
    solutions = solutions + [Dir3 + f for f in listdir(Dir3) if ".csv" in f and "UBC" not in f]
    solutions = solutions + [Dir4 + f for f in listdir(Dir4) if ".csv" in f and "UBC" not in f]
    solutions = solutions + [DirGreeady + f for f in listdir(DirGreeady) if ".csv" in f and "UBC" not in f]

    for solution in solutions:
        print(solution)
        fileName = solution.split("/")[-1]
        print(fileName)
        sourceFiles = []
        targetFiles = []
        if "T" in fileName:
            sourceFiles = fileName.split("-")[0].split("_")[1:]
            targetFiles = fileName.split("-")[1].split("_")[0:2]
        else: 
            if(len(fileName.split("_")) > 8):
                sourceFiles = fileName.split("_")[3:5]
                targetFiles = fileName.split("_")[8:10]  
            else:
                sourceFiles = fileName.split("_")[1:3]
                targetFiles = fileName.split("_")[4:6]
        sln = solution
        source = getWorkload(sourceFiles[0], sourceFiles[1])
        target = getWorkload(targetFiles[0], targetFiles[1])
        output = "./sols/" + fileName


        command='./calc -source {0} -dest {1} -type SN -noOutput -sln {3} >> {2}'.format(source, target, output, sln)
        print(command)
        p = subprocess.Popen([command], shell=True)
        time_for_single_job = time.time()
        p.wait()
        time_for_single_job = time.time() - time_for_single_job

runStuff()




