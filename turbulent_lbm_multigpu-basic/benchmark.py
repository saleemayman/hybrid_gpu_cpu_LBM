#!/usr/bin/python
import os, subprocess, sys, ConfigParser, json, math
# os = function for operating with OS
# subprocess = allows to spawn new processes, connect to their I/O/Error pipes and obtain their codes
# sys = to store command line arguments stored in argv
# ConfigParser = for working with configuration files
# json = a data interchange format based on javascript syntax
# math = gives access to underlying C library function for floating point math  

keys = ['CUBE_X', 'CUBE_Y', 'CUBE_Z', 'SECONDS', 'FPS']#, 'MLUPS', 'BANDWIDTH']
SECTION_BASE = 'EXP'
INI_FILE_DIR = "./output/benchmark/"
MPI_COMMAND = "mpirun"
LBM_COMMAND = "./build/lbm_opencl_dc_mpicxx_release"

def get_average_value( config, key, num_exp ):
    # for a given key in the list keys, it gets the float value for that key and finds the average depending on the number
    # of sections or num_exp
    sum = 0.0
    for exp in range(1,num_exp+1):
        sum += config.getfloat( SECTION_BASE+str(exp), key ) # coerces the option key in the section EXP to a floating point value
    return sum / num_exp
            
def analyse(filenames):
    print "start analysing " , len(filenames), " files." 
    print "files: " , str(filenames)
    config = ConfigParser.ConfigParser()
    
    # gres: contains the analyzation results of all profiling cases (i.e., EXPs)
    gres = dict(); # creates an empty dictionary. A config parser can be treated as a dictionary
    for filename in filenames:
        print "analysing file: ", filename
        config.read(filename)   # reads the filename
        num_exp = len(config.sections())    # returns the number of sections available in the .ini file
        
        # pres: contains the average values of the metrics for profiling case
        pres = dict()
        # get the key of current profiling case
        proc_key = config.getint( SECTION_BASE+str(1), 'NP' )   # coerces the option NP in the section EXP[x] to an integer
        # each .ini file gets a proc_key depending on NP(num_proc) as computed in the benchmarking step
        
        # compute the average value of profiling metrics for the current profiling case
        for key in keys:
             pres[key]= get_average_value( config, key, num_exp)
        
        # for the given NP(proc_key), e.g. 1, 2, 3, ...,the average value is found from all the EXP cases and stored in the dict() gres 
        gres[proc_key] = pres
        
    return gres

def execute(command):
    print "executing command: ", command
    os.system(command) # OS executes the command (a string) in a subshell(shell script launching a new process)

def weak_scaling_benchmark_2d(max_num, num_exp, loops = 100, grid_size_increase_step = 1024, base_domain_length = 0.1 ):
    DOMAIN_LENGTH = base_domain_length
    for num_increase in range(1,max_num+1):
        num_proc = num_increase*num_increase
        # computing the grid size for current benchmark
        x_size = grid_size_increase_step*num_increase
        y_size = x_size
        # generating the string of execution command  
        command_str = MPI_COMMAND + " -n " + str(num_proc)+ "  " + LBM_COMMAND 
        command_str += " -x " + str(x_size) +  " -X " +  str(num_increase) 
        command_str += " -y " + str(y_size) +  " -Y " +  str(num_increase) 
        command_str += " -l " + str(loops)
        command_str +=  " -n " + str(DOMAIN_LENGTH*num_increase) + " -m " + str(DOMAIN_LENGTH*num_increase) + " -p " + str(DOMAIN_LENGTH)
        ini_filename = INI_FILE_DIR + "benchmark_" + str(num_proc)+ ".ini"
        # performing the experiments
        for exp_counter in range(1,num_exp+1):
            f = open(ini_filename, 'a')
            f.write("["+SECTION_BASE+str(exp_counter)+"]\n") # adds the lines 'EXP1', for example, in the output .ini files
            f.write("NP : " + str(num_proc))
            f.write("\n")
            f.close()
            execute(command_str)

def weak_scaling_benchmark_1d(max_num, num_exp, loops = 100, grid_size_increase_step = 32, base_domain_length = 0.1 ):
    DOMAIN_LENGTH = base_domain_length
    for num_increase in range(1,max_num+1):
        num_proc = num_increase # num_proc depends on the input max_num, the 1st input argument of argv
        
        # computing the grid size for current benchmark
        x_size = grid_size_increase_step*num_increase
        y_size = 32
        # generating the string of execution command  
        command_str = MPI_COMMAND + " -n " + str(num_proc)+ "  " + LBM_COMMAND 
        command_str += " -x " + str(x_size) +  " -X " +  str(num_increase) 
        command_str += " -y " + str(y_size) #+  " -Y " +  str(num_increase) 
        command_str += " -l " + str(loops)
        command_str +=  " -n " + str(DOMAIN_LENGTH*num_increase) + " -m " + str(DOMAIN_LENGTH) + " -p " + str(DOMAIN_LENGTH)
        ini_filename = INI_FILE_DIR + "benchmark_" + str(num_proc)+ ".ini" # 
        
        # performing the experiments
        for exp_counter in range(1,num_exp+1):
            f = open(ini_filename, 'a') # mode 'a' for appending indicates how the file is to be opened
            f.write("["+SECTION_BASE+str(exp_counter)+"]\n")
            f.write("NP : " + str(num_proc))
            f.write("\n")
            f.close()
            execute(command_str)

def strong_scaling_benchmark_2d(max_num, num_exp, loops = 100, grid_size = 128, base_domain_length = 0.1 ):
    DOMAIN_LENGTH = base_domain_length
    for num_increase in range(1,max_num+1):
        num_proc = num_increase*num_increase
        # computing the grid size for current benchmark
        x_size = grid_size
        y_size = grid_size
        # generating the string of execution command  
        command_str = MPI_COMMAND + " -n " + str(num_proc)+ " " + LBM_COMMAND 
        command_str += " -x " + str(x_size) +  " -X " +  str(num_increase) 
        command_str += " -y " + str(y_size) +  " -Y " +  str(num_increase) 
        command_str += " -l " + str(loops)
        command_str +=  " -n " + str(DOMAIN_LENGTH) + " -m " + str(DOMAIN_LENGTH) + " -p " + str(DOMAIN_LENGTH)
        ini_filename = INI_FILE_DIR + "benchmark_" + str(num_proc)+ ".ini"
        # performing the experiments
        for exp_counter in range(1,num_exp+1):
            f = open(ini_filename, 'a')
            f.write("["+SECTION_BASE+str(exp_counter)+"]\n")
            f.write("NP : " + str(num_proc))
            f.write("\n")
            f.close()
            execute(command_str)

def strong_scaling_benchmark_1d(max_num, num_exp, loops = 100, grid_size = 32, base_domain_length = 0.1 ):
    DOMAIN_LENGTH = base_domain_length
    for num_increase in range(0,max_num+1):
        num_proc = int(math.pow(2,num_increase))#num_increase*num_increase
        # computing the grid size for current benchmark
        x_size = grid_size
        y_size = grid_size
        # generating the string of execution command  
        command_str = MPI_COMMAND + " -n " + str(num_proc)+ " " + LBM_COMMAND 
        command_str += " -x " + str(x_size) +  " -X " +  str(num_proc) 
        command_str += " -y " + str(y_size)# +  " -Y " +  str(num_increase) 
        command_str += " -l " + str(loops)
        command_str +=  " -n " + str(DOMAIN_LENGTH) + " -m " + str(DOMAIN_LENGTH) + " -p " + str(DOMAIN_LENGTH)
        ini_filename = INI_FILE_DIR + "benchmark_" + str(num_proc)+ ".ini"
        # performing the experiments
        for exp_counter in range(1,num_exp+1):
            f = open(ini_filename, 'a')
            f.write("["+SECTION_BASE+str(exp_counter)+"]\n")
            f.write("NP : " + str(num_proc))
            f.write("\n")
            f.close()
            execute(command_str)

def benchmark(benchmark_strategy, max_num = 1, num_exp = 1):
    benchmark_strategy(max_num, num_exp)

def visualize(profiling_res):
    import pprint   # module for pretty print
    print "profiling results pretty print: "
    pp = pprint.PrettyPrinter(indent=4) # constructs a prettPrint instance
    pp.pprint(profiling_res) # prints the formatted representation of the object profiling_res 
    try:
        import numpy as np  # fundamental package for scientific computing with Python. np is an alias pointing to numpy
        import matplotlib.pyplot as plt # import plotting module 
        ngpus = sorted(profiling_res.keys())    # Return a new sorted list from the items in profiling_res.keys(). Use items() to obtain a
        # dictionary's list of (key, value) pairs
        runtime_values = [] # empty list array
        print "visualizing keys: ", ngpus
        for key in keys:
            # for each key, corresponding to each NP, in the dict() profiling_res, generated from analyse(), extract the values corresponding
            # to the keys in the global variable 'keys'
            values = [float(res[key]) for proc, res in sorted(profiling_res.iteritems())]
            if key is "SECONDS":
                runtime_values = values # time data saved in array for speed-up calculation
            # create a new figure, plot the results for the current key and save
            fig = plt.figure()
            plt.title(key + ' scaling')
            plt.xlabel('# GPUs')
            plt.ylabel(key)
            plt.grid(True)
            plt.plot(ngpus, values, marker='^', linestyle='--', color='g' )
            x1,x2,y1,y2 = plt.axis()
            plt.axis((min(ngpus)-1,max(ngpus)+1,y1,y2))
            filename = INI_FILE_DIR+'plot_'+ key+ '.png'
            fig.savefig(filename)
            print "saved graph: ", filename
        # computing speedup
        speedup_values = []
        for val in runtime_values:
            speedup_values.append(runtime_values[0]/val)    # Adds an item to the end of the list; equivalent to a[len(a):] = [x]
        fig = plt.figure()
        # TODO: implement diffent speedup for weak/strong scaling
        plt.title('Speedup Scaling')
        plt.xlabel('# GPUs')
        plt.ylabel("speedup")
        plt.grid(True)
        #values = [res[key] for proc, res in sorted(profiling_res.iteritems())]
        plt.plot(ngpus, speedup_values, marker='^', linestyle='--', color='g' )
        x1,x2,y1,y2 = plt.axis()
        plt.axis((min(ngpus)-1,max(ngpus)+1,y1,y2))
        filename = INI_FILE_DIR+'plot_speedup.png'
        fig.savefig(filename)
        print "saved graph: ", filename

    except ImportError:
        print "Could not import numpy/matplotlib module"
        for key in keys:
            values = [float(res[key]) for proc, res in sorted(profiling_res.iteritems())]
            print key, ":", values
        print 'MLUPS: ' , [float(res['MLUPS']) for proc, res in sorted(profiling_res.iteritems())]

if __name__ == "__main__":
    #
    import glob
    # finds the pathnames matching a specified pattern
    filenames = glob.glob(INI_FILE_DIR+"*.ini") # string array for all the files in the given dir with .ini extension
    ask = True
    do_benchmark = True
    if len(filenames) != 0: # if above *.ini files exist then do the following 
        while ask:
            print "The benchmark output directory is not empty. What should I do with older files?"
            input_variable = raw_input("(a)ppend, a(r)chive, (d)elete, (u)se?") # take input from command line
            
            # perform tasks according to user input if files already exist in the directory
            if input_variable is "a":
                ask = False
            elif input_variable is "r":
                ask = False
                
                # Try and Except error handling block. Tries to import tarfile, if fails goes into the exception block
                try:
                    import tarfile  # makes it possible to read and write tar archives
                except ImportError: # exception raised when an import statement fails to find the module definition
                    print "not archiving module available."
                    
                import datetime # supplies classes for manipulating dates and times
                now = datetime.datetime.now()
                tar = tarfile.open(INI_FILE_DIR+"archive" + now.strftime("%Y%m%d_%H%M")+ ".tar.gz", "w:gz") # appends the name string
                # now.strftime() returns the date as a string in the specified format which was earlier obtained using datetime.datetime
                
                # archive the files and then remove them
                for f in filenames:
                    print "archiving file: ", f
                    tar.add(f)  # create an uncompressed tar archive from f in the list of filenames
                tar.close()
                for f in filenames:
                    os.remove(f)    # removes the file path in os.remove(PATH). The path is f.
            
            # if input is d, then remove the files
            elif input_variable is "d":
                ask = False
                for f in filenames:
                    print "removing file: ", f
                    os.remove(f)
                    
            # if input is u, then do not do benchmarking and analyse the available files
            elif input_variable is "u":
                ask = False
                do_benchmark = False
            else:
                print "wrong input."

    # if the path './output/benchmark/' does not exist, i.e., no solutions run yet, then create the defined path for outputs
    if not os.path.exists(INI_FILE_DIR): # checking if the object is meaningful or not. Used for testing non-numerical values
        os.makedirs(INI_FILE_DIR)
        
    # do benchmarking if TRUE
    if do_benchmark:
        # get the required arguments from the list of strings on the command-line
        max_num = int(sys.argv[1])
        num_exp = int(sys.argv[2])
        MPI_COMMAND = sys.argv[3]
        LBM_COMMAND = sys.argv[4]
        BENCHMARK_STRATEGY = str(sys.argv[5])
        
        # perform the specified benchmarking scheme by calling the subroutine benchmark()
        print "benchmark strategy: ", BENCHMARK_STRATEGY
        if BENCHMARK_STRATEGY == "weak":
            #benchmark(weak_scaling_benchmark_2d, max_num, num_exp) # commented in the original code as well
            benchmark(weak_scaling_benchmark_1d, max_num, num_exp)
        elif BENCHMARK_STRATEGY == "strong":
            benchmark(strong_scaling_benchmark_1d, max_num, num_exp)
        else:
            print "Unknown benchmarking strategy!"
            sys.exit(0) # exits python, same as exit()
            # integer gives the exit status (default zero), zero=successful termination, nonzero=abnormal termination
                        
    # once benchmarking is complete, analyse the output files
    filenames = glob.glob(INI_FILE_DIR+"*.ini")
    res = analyse(filenames)
    
    print "RES"
    # for each key corresponding to each NP in res(or gres) the below loop adds the sub-key MLUPS 
    for p in range(1,len(res)+1):
        res[p]['MLUPS'] = res[p]['CUBE_X'] * res[p]['CUBE_Y'] * res[p]['CUBE_Z'] * res[p]['FPS'] * 0.000001
        
    # saving the results in json format
    analysation_file_name = INI_FILE_DIR + "results.txt"
    
    with open(analysation_file_name,'w') as outfile:    # opens the result file and keeps it open while the inside statements are executed.
        # once done, calls the __exit__() object to close the file. Similar to try-finally block but less verbose
        # the file is opened for writing ('w'=writing, 'r'=reading)
        json.dump(res,outfile, indent = 4) # takes the python object/dictionary res and serializes it to JSON format via a conversion table
        print "saved analysation results in file:", analysation_file_name
    
    visualize(res)
