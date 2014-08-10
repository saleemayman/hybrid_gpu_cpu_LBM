#!/usr/bin/python
import os, subprocess, sys, shutil, math

MPI_COMMAND = "mpirun"
LBM_COMMAND = "./build/lbm_opencl_dc_mpicxx_release"
SCALASCA_ANALYZE_COMMAND = "scalasca -analyze "

def generate_mpi_command_lbm(num_proc, grid_size, loops = 100, base_domain_length = 0.1 ):
	DOMAIN_LENGTH = base_domain_length

	# computing the grid size for current benchmark
	x_size = grid_size
	y_size = grid_size
	# generating the string of execution command  
	command_str = MPI_COMMAND + " -n " + str(num_proc)+ " " + LBM_COMMAND 
	command_str += " -x " + str(x_size) +  " -X " +  str(num_proc) 
	command_str += " -y " + str(y_size)# +  " -Y " +  str(num_increase) 
	command_str += " -l " + str(loops)
	command_str +=  " -n " + str(DOMAIN_LENGTH) + " -m " + str(DOMAIN_LENGTH) + " -p " + str(DOMAIN_LENGTH)

	command_str = SCALASCA_ANALYZE_COMMAND + command_str

	# performing the experiments
	execute(command_str)

#def benchmark(benchmark_strategy, num_proc):
#	benchmark_strategy(num_proc)

def execute(command):
	print "executing command: ", command
	os.system(command)

if __name__ == "__main__":
	import glob

	# check for existing profiled data (delete or archive them)
	filenames_old = glob.glob("scorep*")

	ask = True
	do_profiling = True
	if len(filenames_old) != 0:
		while ask:
			print "Scorep folders exist. What do you want to do with them?"
			input_variable = raw_input("a(r)chive, (d)elete?")

			# compress them to tar.gz and delete the original folder and the contents
			if input_variable is "r":
				ask = False
				try:
					import tarfile
				except ImportError:
					print "not archiving module available."
				import datetime
				now = datetime.datetime.now()
				tar = tarfile.open("profiling_archive" + now.strftime("%Y%m%d_%H%M")+ ".tar.gz", "w:gz")
				for f in filenames_old:
					print "archiving file: ", f
					tar.add(f)
				tar.close()
				for f in filenames_old:
					shutil.rmtree(f)

			# delete the folders and the contents
			elif input_variable is "d":
				ask = False
				for f in filenames_old:
					print "removing file: ", f
					shutil.rmtree(f)
			else:
				print "wrong input."

	if do_profiling:
		PROFILER = sys.argv[1]
		do_trace = sys.argv[2]
		num_proc = int(sys.argv[3])
		MPI_COMMAND = sys.argv[4]
		LBM_COMMAND = sys.argv[5]
		grid_size = int(sys.argv[6])
		#loops = int(sys.argv[7])

		# construct instrumentation, compile and examine commands
		command_clean = "make clean"
		command_compile = "scons --profiler=" + PROFILER
		command_examine = "scalasca -examine -s "
		command_display_report = "head -n 30 "

		# append analyze command if trace events are used
		if do_trace == "trace":
			SCALASCA_ANALYZE_COMMAND = SCALASCA_ANALYZE_COMMAND + "-q -t "

		# do a make clean
		os.system(command_clean)

		# compile code with instrumentation
		print "\n* * * * * Code instrumentation started * * * * * "
		os.system(command_compile)

		# execute instrument code 
		print "\n* * * * * Execute instrumented code * * * * * "
		generate_mpi_command_lbm(num_proc, grid_size)
		
		# analyze profiled data using scalasca
		filenames_new = glob.glob("scorep_*")

		# examine profiled data and display summary
		for profile in range(0, len(filenames_new)):
			command_examine = command_examine + filenames_new[profile]
			command_display_report = command_display_report + filenames_new[profile] + "/scorep.score"

			# run scalasca examine command
			print "\n* * * * * Examine using scalasca * * * * * "
			execute(command_examine)

			# display examined report; 1st 20 lines
			print "\n* * * * * Profiling summary * * * * * "
			execute(command_display_report)




