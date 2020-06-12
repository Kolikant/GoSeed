#!/usr/bin/python


import sys
import subprocess
import datetime
from timeit import default_timer as timer
import time

if len(sys.argv)!=2:
		print('useage: \"python3 june2020_ariel_tests.py <seed>\"')
		exit()

seed=int(sys.argv[1])
epsilon_list=[0, 2]#, 10, 15]
trafficLimit=[10, 20, 25, 33, 50]
# grouping_factor_list=[1, 2, 4, 8, 16]
k_list=[8, 10, 12, 13]
time_limit=21600#?
threads=38#?

#UBC:

def run_UBC_cont_depth1():
	start=timer()
	avg_cont_size=4194304
	depth=1
	testCases = [
					# ('data/testData/cannotDeleteAllDuplicates/B_f1_depth1_118_118.csv', 'data/testData/cannotDeleteAllDuplicates/B_f2_depth1_118_118.csv')
				('data/testData/fullExample/B_heuristic_depth1_121_125.csv', 'data/testData/fullExample/B_heuristic_depth1_122_122.csv'),
				('data/testData/fullMedium/B_heuristic_depth1_436_440.csv', 'data/testData/fullMedium/B_heuristic_depth1_438_438.csv'),
				# ('data/testData/fullBig/B_heuristic_depth1_216_220.csv', 'data/testData/fullBig/B_heuristic_depth1_219_219.csv')
			]
	for epsilon in epsilon_list:
		output_file='june2020_depth1_cont_e{0}_s{1}.csv'.format(epsilon,seed)
		handler_output_file=open(output_file, 'a+')
		handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
		handler_output_file.write('Input file,Deduplication level,Depth,System start,System end,filter/grouping factor,avg block/container size,Number of blocks/containers,Number of files,M fraction,M,M fraction actual,M actual,Epsilon fraction,Epsilon,Replication,Replication fraction,Seed,Threads,Time limit,Status,Total time,Solver time\n')
		handler_output_file.flush()
		handler_output_file.close
		for testCase in testCases:
			file_system_start=testCase[0].split("_")[3]
			file_system_end=testCase[0].split("_")[4]
			for m in trafficLimit:
				write_sol='solutions/file_to_move_UBC_'+'GoSeedBlocksAriel{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(testCase[0].split("/")[-1], output_file, m, epsilon, 'write_solution', 8, time_limit, seed, threads, avg_cont_size, depth, file_system_start, file_system_end)+'.csv'												#./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
				command='./GoSeedBlocksAriel {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13}'.format(testCase[0],  testCase[1], output_file, m, epsilon, write_sol, 8, time_limit, seed, threads, avg_cont_size, depth, file_system_start, file_system_end)
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





