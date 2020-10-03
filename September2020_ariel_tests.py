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
epsilon_list=[5]
trafficLimit=[50]
# grouping_factor_list=[1, 2, 4, 8, 16]
k_list=[8, 10, 12, 13]
time_limit=21600#?
threads=38#?

#UBC:

def run_UBC_cont_depth1():
    start=timer()
    avg_cont_size=4194304
    depth=1
    # mishmashOfFives = [
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_121_125.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_216_220.csv'),
    #                     ('data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv', 'data/testData/5SystemLoad/B_heuristic_depth1_436_440.csv'),
    #                 ]

    mishmashOfFilteredFives = [
                    ('data/testData/filtered/B_dedup_k4_001_005.csv', 'data/testData/filtered/B_dedup_k4_001_005.csv'),
                    ('data/testData/filtered/B_dedup_k4_001_005.csv', 'data/testData/filtered/B_dedup_k4_006_010.csv'),
                    ('data/testData/filtered/B_dedup_k4_001_005.csv', 'data/testData/filtered/B_dedup_k4_011_015.csv'),
                    ('data/testData/filtered/B_dedup_k4_006_010.csv', 'data/testData/filtered/B_dedup_k4_001_005.csv'),
                    ('data/testData/filtered/B_dedup_k4_006_010.csv', 'data/testData/filtered/B_dedup_k4_006_010.csv'),
                    ('data/testData/filtered/B_dedup_k4_006_010.csv', 'data/testData/filtered/B_dedup_k4_011_015.csv'),
                    ('data/testData/filtered/B_dedup_k4_011_015.csv', 'data/testData/filtered/B_dedup_k4_001_005.csv'),
                    ('data/testData/filtered/B_dedup_k4_011_015.csv', 'data/testData/filtered/B_dedup_k4_006_010.csv'),
                    ('data/testData/filtered/B_dedup_k4_011_015.csv', 'data/testData/filtered/B_dedup_k4_011_015.csv'),
                ]

    mishmashOfFilteredFivesWithFifty = [
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280..csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_331_340.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_061_070.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280..csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_331_340.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_061_070.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280..csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_331_340.csv'),
                    ('data/toFilter/B_heuristic_depth1_k10_351_400.csv', 'data/toFilter/B_heuristic_depth1_k9_061_070.csv')
                ]

    filteredTen = [
                ('data/toFilter/B_heuristic_depth1_k10_351_360.csv', 'data/toFilter/B_heuristic_depth1_k10_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_331_340.csv', 'data/toFilter/B_heuristic_depth1_k10_351_360.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_061_070.csv', 'data/toFilter/B_heuristic_depth1_k10_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_271_280.csv', 'data/toFilter/B_heuristic_depth1_k10_061_070.csv'),
            ]    

    filtered25 = [
                ('data/toFilter/B_heuristic_depth1_k10_051_075.csv', 'data/toFilter/B_heuristic_depth1_k10_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_151_175.csv', 'data/toFilter/B_heuristic_depth1_k10_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_051_075.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_051_075.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_151_175.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_151_175.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv')
            ]        

    filtered100 = [
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_100.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv')
            ]

    cocos1 = [
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_001_200.csv'),
                ('data/toFilter/B_heuristic_depth1_k9_001_100.csv', 'data/toFilter/B_heuristic_depth1_k9_001_500.csv')
    ]

    cocos9 = [
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_001_200.csv'),
                ('data/toFilter/B_heuristic_depth1_k8_001_100.csv', 'data/toFilter/B_heuristic_depth1_k8_001_500.csv')
    ]

    cocos10 = [
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_001_200.csv'),
                ('data/toFilter/B_heuristic_depth1_k11_001_500.csv', 'data/toFilter/B_heuristic_depth1_k11_001_500.csv')
    ]

    cocos2 = [
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_200.csv', 'data/toFilter/B_heuristic_depth1_k10_001_500.csv')
    ]

    cocos8 = [
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_151_175.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_051_075.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_331_340.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_061_070.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_271_280.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_351_400.csv'),
                ('data/toFilter/B_heuristic_depth1_k10_001_500.csv', 'data/toFilter/B_heuristic_depth1_k10_001_200.csv'),
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
                
    output_file = machine + 'june2020_depth1_cont.csv'
    handler_output_file=open(output_file, 'a+')
    handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
    handler_output_file.write('v1First, v1Last, v1NumFiles, v2First, v2Last, v2NumFiles, Deduplication level, Depth, filter/grouping factor, avg block/container size, Number of blocks/containers, T fraction, T, M fraction actual, M actual, minimum migration fraction, minimum migration, Replication, Replication fraction, traffic fraction actual, traffic actual, volume change fraction, volume change, Seed, Threads, Time limit, Status, Total time, Solver time, Preprocess time, variable_number, constraint_number, source_block_number, target_block_number, intersect_block_number\n')
    handler_output_file.flush()
    handler_output_file.close
    for epsilon in epsilon_list:
        for testCase in testCases:
            file_system_start = testCase[0].split("_")[4]
            file_system_end = testCase[0].split("_")[5].split(".")[0]
            k_filter = testCase[0].split("_")[3].split('k')[1]

            for m in trafficLimit:
                if(epsilon >= m):
                    continue
                write_sol='solutions/file_to_move_UBC_'+'GoSeedBlocksAriel{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(testCase[0].split("/")[-1], output_file, m, epsilon, 'write_solution', 8, time_limit, seed, threads, avg_cont_size, depth, file_system_start, file_system_end)+'.csv'                                                #./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
                command='./GoSeedBlocksAriel {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13}'.format(testCase[0],  testCase[1], output_file, m, epsilon, write_sol, k_filter, time_limit, seed, threads, avg_cont_size, depth, file_system_start, file_system_end)
                p = subprocess.Popen([command], shell=True)
                time_for_single_job = time.time()
                p.wait()
                time_for_single_job = time.time() - time_for_single_job
                print('just finished: ','file:',file,'m:',m,'took:',time_for_single_job)
        end = timer()
    handler_output_file=open(output_file, 'a+')
    handler_output_file.write('end: '+str(datetime.datetime.now())+'\n')
    handler_output_file.write('the test ran for: '+str(end-start)+'\n')
    handler_output_file.flush()
    handler_output_file.close


run_UBC_cont_depth1()





