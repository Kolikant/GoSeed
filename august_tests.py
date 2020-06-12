#!/usr/bin/python


import sys
import subprocess
import datetime
from timeit import default_timer as timer
import time

if len(sys.argv)!=3:
		print('useage: \"python3 august_tests.py <epsilon> <seed>\"')
		exit()

epsilon=int(sys.argv[1])#? epsilon 1 is risky because after aggregate the actual m will be out of bounds.
seed=int(sys.argv[2])
m_list=[10,20,25,33,50]
grouping_factor_list=[1,2,4,8,16]
k_list=[8,10,12,13]
time_limit=21600#?
threads=38#?

#UBC:

def run_UBC_cont_depth1():
	start=timer()
	print('UBC-CONT')
	avg_cont_size=4194304
	depth=1
	file_list=['B_heuristic_depth1_001_050_4194304_D0_P0.csv','B_heuristic_depth1_051_100_4194304_D0_P0.csv']
	file_list+=['B_heuristic_depth1_001_{0}_4194304_D0_P0.csv'.format(end_sys) for end_sys in ['100','200','500']]
	output_file='august_gurobi_UBC_depth1_cont_e{0}_s{1}.csv'.format(epsilon,seed)
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('Input file,Deduplication level,Depth,System start,System end,filter/grouping factor,avg block/container size,Number of blocks/containers,Number of files,M fraction,M,M fraction actual,M actual,Epsilon fraction,Epsilon,Replication,Replication fraction,Seed,Threads,Time limit,Status,Total time,Solver time\n')
	handler_output_file.flush()
	handler_output_file.close
	for file in file_list:
		file_system_start=file[19:22]
		file_system_end=file[23:26]
		for m in m_list:
			for gf in grouping_factor_list:
				write_sol='solutions/file_to_move_UBC_'+'main_UBC_CONT_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(file,output_file,m,epsilon,'write_solution',gf,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end)+'.csv'												#./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
				command='./main_UBC_CONT {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.format(file,output_file,m,epsilon,write_sol,gf,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end)
				p = subprocess.Popen([command], shell=True)
				time_for_single_job = time.time()
				p.wait()
				time_for_single_job = time.time() - time_for_single_job
				print('just finished: ','file:',file,'m:',m,'gf:',gf,'took:',time_for_single_job)
	end = timer()
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('end: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('the test ran for: '+str(end-start)+'\n')
	handler_output_file.flush()
	handler_output_file.close






def run_UBC_filter_depth1():
	start=timer()
	print('UBC-FILTER')
	avg_cont_size=65536
	depth=1
	file_list=['B_heuristic_depth1_k_001_050.csv','B_heuristic_depth1_k_001_050.csv']
	file_list+=['B_heuristic_depth1_k_001_{0}.csv'.format(end_sys) for end_sys in ['100','200','500']]
	output_file='august_gurobi_UBC_depth1_filter_e{0}_s{1}.csv'.format(epsilon,seed)
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('Input file,Deduplication level,Depth,System start,System end,filter/grouping factor,avg block/container size,Number of blocks/containers,Number of files,M fraction,M,M fraction actual,M actual,Epsilon fraction,Epsilon,Replication,Replication fraction,Seed,Threads,Time limit,Status,Total time,Solver time\n')
	handler_output_file.flush()
	handler_output_file.close
	for file_no_k in file_list:
		file_system_start=file_no_k[21:24]
		file_system_end=file_no_k[25:28]
		for m in m_list:
			for k in k_list:
				file=file_no_k[0:20]+str(k)+file_no_k[20::]
				write_sol='solutions/file_to_move_UBC_'+'main_UBC_BLOCK_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(file,output_file,m, epsilon,'write_solution',k,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end) +'.csv'												#./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
				command='./main_UBC_BLOCK {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.format(file,output_file,m,epsilon,write_sol,k,time_limit,seed,threads,avg_cont_size, depth,file_system_start,file_system_end)
				p = subprocess.Popen([command], shell=True)
				time_for_single_job = time.time()
				p.wait()
				time_for_single_job = time.time() - time_for_single_job
				print('just finished: ','file:',file,'m:',m,'k:',k,'took:',time_for_single_job)
	end = timer()
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('end: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('the test ran for: '+str(end-start)+'\n')
	handler_output_file.flush()
	handler_output_file.close



#####################################################################################################################################################################################

#FSL:

def run_FSL_cont_depth1():
	start=timer()
	print('FSL-CONT')
	avg_cont_size=4194304
	depth=1
	file_list=['B_heuristic_depth1_001_200_4194304_D0_P0.FSL.macos.D.csv','B_heuristic_depth1_001_200_4194304_D0_P0.FSL.macos.S.csv']
	file_list+=['B_heuristic_depth1_001_270_4194304_D0_P0.FSL.homes.D.csv', 'B_heuristic_depth1_001_117_4194304_D0_P0.FSL.homes.S.csv']#?9 users over a month&9 users everyweekend over 13 weeks
	output_file='august_gurobi_FSL_depth1_cont_e{0}_s{1}.csv'.format(epsilon,seed)
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('Input file,Deduplication level,Depth,System start,System end,filter/grouping factor,avg block/container size,Number of blocks/containers,Number of files,M fraction,M,M fraction actual,M actual,Epsilon fraction,Epsilon,Replication,Replication fraction,Seed,Threads,Time limit,Status,Total time,Solver time\n')
	handler_output_file.flush()
	handler_output_file.close
	for file in file_list:
		file_system_start=file[19:22]
		file_system_end=file[23:26]
		for m in m_list:
			for gf in grouping_factor_list:
				write_sol='solutions/file_to_move_FSL'+'main_UBC_CONT_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(file,output_file,m,epsilon,'write_solution',gf,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end)+'.csv'												#./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
				command='./main_UBC_CONT {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.format(file,output_file,m,epsilon,write_sol,gf,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end)
				p = subprocess.Popen([command], shell=True)
				time_for_single_job = time.time()
				p.wait()
				time_for_single_job = time.time() - time_for_single_job
				print('just finished: ','file:',file,'m:',m,'gf:',gf,'took:',time_for_single_job)
	end = timer()
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('end: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('the test ran for: '+str(end-start)+'\n')
	handler_output_file.flush()
	handler_output_file.close






def run_FSL_filter_depth1():
	start=timer()
	print('FSL-FILTER')
	avg_cont_size=65536
	depth=1
	file_list=['B_heuristic_depth1_k_001_200.FSL.macos.D.csv','B_heuristic_depth1_k_001_200.FSL.macos.S.csv']
	file_list+=['B_heuristic_depth1_k_001_270.FSL.homes.D.csv','B_heuristic_depth1_k_001_117.FSL.homes.S.csv']
	output_file='august_gurobi_FSL_depth1_filter_e{0}_s{1}.csv'.format(epsilon,seed)
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('start: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('Input file,Deduplication level,Depth,System start,System end,filter/grouping factor,avg block/container size,Number of blocks/containers,Number of files,M fraction,M,M fraction actual,M actual,Epsilon fraction,Epsilon,Replication,Replication fraction,Seed,Threads,Time limit,Status,Total time,Solver time\n')
	handler_output_file.flush()
	handler_output_file.close
	for file_no_k in file_list:
		file_system_start=file_no_k[21:24]
		file_system_end=file_no_k[25:28]
		for m in m_list:
			for k in k_list:
				file=file_no_k[0:20]+str(k)+file_no_k[20::]
				write_sol='solutions/file_to_move_FSL_'+'main_UBC_BLOCK_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}'.format(file,output_file,m, epsilon,'write_solution',k,time_limit,seed,threads,avg_cont_size,depth,file_system_start,file_system_end) +'.csv'												#./main_UBC_CONT {file name} {benchmarks output file name} {M} {epsilon} {yes/no (write solution to optimization_solution.txt)} {k filter factor} {model time limit in seconds} {seed} {threads} {avg block size} {depth} {file_system_start} {file_system_end}
				command='./main_UBC_BLOCK {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12}'.format(file,output_file,m,epsilon,write_sol,k,time_limit,seed,threads,avg_cont_size, depth,file_system_start,file_system_end)
				p = subprocess.Popen([command], shell=True)
				time_for_single_job = time.time()
				p.wait()
				time_for_single_job = time.time() - time_for_single_job
				print('just finished: ','file:',file,'m:',m,'k:',k,'took:',time_for_single_job)
	end = timer()
	handler_output_file=open(output_file, 'a+')
	handler_output_file.write('end: '+str(datetime.datetime.now())+'\n')
	handler_output_file.write('the test ran for: '+str(end-start)+'\n')
	handler_output_file.flush()
	handler_output_file.close











run_UBC_cont_depth1()
run_UBC_filter_depth1()





