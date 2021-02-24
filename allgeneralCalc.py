

import sys
import subprocess
import datetime
from timeit import default_timer as timer
import time
import socket
from os import listdir
from os.path import isfile, join

if len(sys.argv)!=1:
    print('useage: \"python3 runCalc.py\"')
    exit()

slnDir = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/FullMigration/forCalc/"
dest = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/FullMigration/calcResults/"

def runStuff():
    solutions = [slnDir + f for f in listdir(slnDir) if ".csv" in f]

    for solution in solutions:
        fileName = solution.split("/")[-1]
        output = dest + fileName

        command='/nfs_share/storage-simulations/Arielk/CostCalcGeneral/calc -file {0} >> {1}'.format(solution, output)
        p = subprocess.Popen([command], shell=True)
        time_for_single_job = time.time()
        p.wait()
        time_for_single_job = time.time() - time_for_single_job

runStuff()




