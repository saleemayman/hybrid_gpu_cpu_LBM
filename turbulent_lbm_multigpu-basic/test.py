import os, subprocess, sys, ConfigParser, json, math
keys = ['CUBE_X', 'CUBE_Y', 'CUBE_Z', 'SECONDS', 'FPS']#, 'MLUPS', 'BANDWIDTH']
SECTION_BASE = 'EXP'
INI_FILE_DIR = "./output/benchmark/"

def get_average_value( config, key, num_exp ):
    # for a given key in the list keys, it gets the float value for that key and finds the average depending on the number
    # of sections or num_exp
    sum = 0.0
    for exp in range(1,num_exp+1):
        sum += config.getfloat( SECTION_BASE+str(exp), key ) # coerces the option key in the section EXP to a floating point value
    return sum / num_exp

def visualize(profiling_res):
    import pprint   # module for pretty print
    print "profiling results pretty print: "
    pp = pprint.PrettyPrinter(indent=4) # constructs a prettPrint instance
    #pp.pprint(profiling_res) # prints the formatted representation of the object profiling_res 
    try:
        import numpy as np  # fundamental package for scientific computing with Python. np is an alias pointing to numpy
        import matplotlib.pyplot as plt # import plotting module 
        ngpus = sorted(profiling_res.keys())    # Return a new sorted list from the items in profiling_res.keys(). Use items() to obtain a
        # dictionary's list of (key, value) pairs
        runtime_values = [] # empty list array
        print "visualizing keys: ", ngpus
        #print "profiling_res: ", profiling_res
        for key in keys:
            # for each key, corresponding to each NP, in the dict() profiling_res, generated from analyse(), extract the values corresponding
            # to the keys in the global variable 'keys'
            values = [float(res[key]) for proc, res in sorted(profiling_res.iteritems())]
            print "values: ", values
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
            plt.axis((min(ngpus)-1,max(ngpus)+1,y1,y2)) # axes extent
            filename = INI_FILE_DIR+'plot_'+ key+ '.png'
            fig.savefig(filename)
            print "saved graph: ", filename
        # computing speedup
        speedup_values = []
        for val in runtime_values:
            speedup_values.append(runtime_values[0]/val)    # Adds an item to the end of the list; equivalent to a[len(a):] = [x]
        
        # plot figure for speed-up
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
        print "sections: ", len(config.sections())
        # pres: contains the average values of the metrics for profiling case
        pres = dict()
        # get the key of current profiling case
        proc_key = config.getint( SECTION_BASE+str(1), 'NP' )   # coerces the option NP in the section EXP[x] to an integer
        # each .ini file gets a proc_key depending on NP(num_proc) as computed in the benchmarking step
        
        # compute the average value of profiling metrics for the current profiling case
        for key in keys:
             pres[key]= get_average_value( config, key, num_exp)
             print "pres: ", pres
        # for the given NP(proc_key), e.g. 1, 2, 3, ...,the average value is found from all the EXP cases and stored in the dict() gres 
        gres[proc_key] = pres
        print "proc_key= ", proc_key
        print "gres: ", gres
    return gres

if __name__ == "__main__":
    import glob
    print "\n....script started....\n"

    filenames = glob.glob(INI_FILE_DIR+"*.ini")
    res = analyse(filenames)
    #print "RES", res
    
    # for each key corresponding to each NP in res(or gres) the below loop adds the sub-key MLUPS 
    for p in range(1,len(res)+1):
        res[p]['MLUPS'] = res[p]['CUBE_X'] * res[p]['CUBE_Y'] * res[p]['CUBE_Z'] * res[p]['FPS'] * 0.000001
    analysation_file_name = INI_FILE_DIR + "results.txt"

    with open(analysation_file_name,'w') as outfile:    # opens the result file and keeps it open while the inside statements are executed.
        # once done, calls the __exit__() object to close the file. Similar to try-finally block but less verbose
        # the file is opened for writing ('w'=writing, 'r'=reading)
        json.dump(res,outfile, indent = 4) # takes the python object/dictionary res and serializes it to JSON format via a conversion table
        print "saved analysation results in file:", analysation_file_name

    #print "RES", res
    
    visualize(res)
