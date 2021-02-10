#!/usr/bin/python


import sys
import subprocess
import datetime
from timeit import default_timer as timer
import time
import socket

if len(sys.argv)!=1:
    print('useage: \"python3 runCalc.py\"')
    exit()

def runStuff():
    sources = ['/nfs_share/storage-simulations/Roei/traces/UBC/B_heuristic_depth1_001_500.csv']
    targets = [
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_151_175.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_051_075.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_331_340.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_061_070.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_271_280.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_351_400.csv',
                '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_001_200.csv',
                '/nfs_share/storage-simulations/Roei/traces/UBC/B_heuristic_depth1_001_500.csv'
            ]
    
    configs = [ 
        '40_10',
        '40_5',
        '50_10',
        '50_5',
        '60_10',
        '60_5',
    ]
    
# ('/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_001_200.csv',
# '/nfs_share/storage-simulations/Roei/traces/divisions/ariel_runs/B_heuristic_depth1_001_500_351_400.csv',
# './sols/k11_001_200_k11_351_400_70_25',
# '/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/October/Cocos2/k10_001_200_k10_351_400_70_25.csv' ),
    
    for source in sources:
        for target in targets:
            for config in configs:
                banana = "k11_" + "_".join(source.split("/")[-1].split(".")[0].split("_")[-2:]) + "_k11_" + "_".join(target.split("/")[-1].split(".")[0].split("_")[-2:]) + "_" + config
                outPutFile = "./sols/" + banana  
                slnFile = "/nfs_share/storage-simulations/Arielk/GoSeedGeneral/GoSeed/solutionsProcessed/October/Cocos10/" + banana + ".csv"
                command='./calc -source {0} -dest {1} -type SN -noOutput -sln {3} >> {2}'.format(source, target, outPutFile, slnFile)
                print(command)
                p = subprocess.Popen([command], shell=True)
                time_for_single_job = time.time()
                p.wait()
                time_for_single_job = time.time() - time_for_single_job


runStuff()





