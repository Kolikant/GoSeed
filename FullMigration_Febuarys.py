#!/usr/bin/python


import sys
import subprocess
import datetime
from timeit import default_timer as timer
import time
import socket

if len(sys.argv)!=2:
    print('useage: \"python3 june2020_ariel_tests.py <seed>\"')
    exit()

seed=int(sys.argv[1])
epsilon_list=[5, 10, 20]
trafficLimit=[10, 20, 40, 70]
# grouping_factor_list=[1, 2, 4, 8, 16]
time_limit=21600#?
threads=38#?

#UBC:

def run_UBC_cont_depth1():
    start=timer()
    avg_cont_size=4194304
    depth=1

    catalina2 = [
                ('./data/volumeList/heavy3',  './data/volumeList/heavy3'),
        ]

    testCases = []
    machine = socket.gethostname()
    if(machine == "cocos1"):
        testCases += cocos1
    if(machine == "cocos2"):
        testCases += cocos2
    if(machine == "cocos8"):
        testCases += cocos8
    if(machine == "cocos9"):
        testCases += cocos9
    if(machine == "cocos10"):
        testCases += cocos10
    if(machine == "catalina2"):
        testCases += catalina2
                
    for epsilon in epsilon_list:
        for testCase in testCases:
            for m in trafficLimit:
                if(epsilon >= m):
                    continue
                command='./GoSeedBlocksFullMigration' + ' {0} {1} {2} {3} {4} {5}'.format(testCase[0], m, epsilon, time_limit, seed, threads)
                print(command)
                p = subprocess.Popen([command], shell=True)
                time_for_single_job = time.time()
                p.wait()
                time_for_single_job = time.time() - time_for_single_job
        end = timer()

run_UBC_cont_depth1()





