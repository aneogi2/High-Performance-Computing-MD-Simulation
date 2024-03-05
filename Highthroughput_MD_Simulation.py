#Import Modules
from shutil import copy, rmtree
import os
from natsort import natsorted
import numpy as np 
import re
from glob import glob
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from itertools import combinations
from math import *

class CalcGen(object):
    """
    Creates the input geometry file and calculation directories for the run. Assumes all geometry files are orthogonal
    """

    def __init__(self,scriptDir,df,atom_style='atomic'):  
        
        self.scriptDir = scriptDir
        #self.inputGeo = inputGeo
        #self.inputStruct = LammpsData.from_file(self.inputGeo ,atom_style=atom_style).structure
        #self.amorphors = amorphors
        self.dataframe = df
            
            
            
    def genFriction(self,interfaceDirs,outdir,velocity=0.1,time=20,time_restart=5): # Time in nanoseconds
        
        try:
            rmtree(outdir)
        except:
            pass

        os.mkdir(outdir)

        data = open("{}/in.fric".format(self.scriptDir),"r").readlines()
        data_restart = open("{}/restart.in".format(self.scriptDir),"r").readlines()

        for direc in interfaceDirs:

            PT = direc.split("/")[-1].split("_")
            p = float(PT[0])
            T = float(PT[1])
            path = "{}/{}_{}".format(outdir,p,T)
            
            os.mkdir(path)
            data[4] = "read_data      Si_equi.geo\n" 
            data[44] = "variable      top_load equal {}\n".format(p)    
            data[47]  = "variable      velocity equal {}\n".format(velocity)
            data[40]  = "variable      Tapp equal {}\n".format(T)
            #data[152] = "run           {}\n".format(time*100000)
            open("{}/friction.in".format(path),"w").writelines(data)
            
            data_restart[4] = "read_restart      restart.equil\n"
            data_restart[44] = "variable      top_load equal {}\n".format(p)
            data_restart[47] = "variable      velocity equal {}\n".format(velocity)
            data_restart[40] = "variable      Tapp equal {}\n".format(T)
            #data_restart[127] = "run           {}\n".format(time_restart*100000)
            open("{}/restart.in".format(path),"w").writelines(data)
            
            
            copy("{}/Si_equi.geo".format(self.scriptDir), path)
            copy("{}/Si.sw".format(self.scriptDir), path)




        
    def job_script(self,outfile,directories,jobname="Si_highT",cores=384,queue="knl"):
        try:
            os.remove(outfile)
        except:
            pass
        

        with open(outfile,"a") as outfile:
            outfile.write("#!/bin/bash\n")
            outfile.write("#SBATCH -N {}\n".format(len(directories)*ceil(cores/64)))
            outfile.write("#SBATCH -C {}\n".format(queue))
            outfile.write("#SBATCH -A m3794\n")
            outfile.write("#SBATCH -q regular\n")
            outfile.write("#SBATCH -J {}\n".format(jobname))
            outfile.write("#SBATCH -t 16:00:00\n")
            outfile.write("\n\n")
            outfile.write("module load fftw adios2 gsl")
            outfile.write("\n\n")
            outfile.write('export LD_LIBRARY_PATH="/global/common/sw/cray/cnl7/haswell/adios2/2.5.0/intel/19.0.3.199/rjsjd4c/lib64/:$LD_LIBRARY_PATH"')
            outfile.write("\n\n")
            outfile.write('lammps="/global/cfs/cdirs/m1917/blast_ff/bin/lammps-3Mar20/bin/lmp_cori_parallel"')
            outfile.write("\n\n")
            for direc in directories:
                outfile.write("cd {}\n".format(direc))
                outfile.write("srun -N {} -n{} -c2 --cpu_bind=cores $lammps -in friction.in &\n".format(ceil(cores/64),cores))
            outfile.write("wait")

'''
Test Case
'''
# Creating Calculation Folders based on Pressure and Temperature

newDataPoints = []
T = np.linspace(1100,1100,1)
P = np.linspace(9.6,9.9,4)
for p in P:
    for t in T:
        newDataPoints.append([t,p])
DF = pd.DataFrame(np.array(newDataPoints),columns=["T","P"])
DF
root_path = "{}/calculation/interface_finescan".format(os.getcwd())

#isExist = os.path.exists(root_path)

#if not isExist:
for T,p in newDataPoints:
    path = os.path.join(root_path,("{}_{}".format(p,T)))
    os.makedirs(path)
direcGen = CalcGen("{}/input_scripts".format(os.getcwd()),DF)
out_dir = "{}/calculation".format(os.getcwd())
velocity = 0.1
directories = []
for direc in natsorted(glob("{}/interface_finescan/*".format(out_dir))):
#    if os.path.exists("{}/out.geo".format(direc)):
    directories.append(direc)        

# Create directories with input file
outdir = "{}/calculation/v{}_finescan".format(os.getcwd(),velocity)
direcGen.genFriction(directories,outdir,velocity,time=20,time_restart=5)
# Create HPC jobscripts based on number of simulation directories
directs = []
for direc in natsorted(glob("{}/v0.1_finescan/*".format(out_dir))):
    if not os.path.exists("{}/log.lammps".format(direc)):
        directs.append(direc)
count = 70 # Modify according to the computing capacity. Specifies that each job script will have 70 simulations.
chunks1 = [directs[i:i + count] for i in range(0, len(directs), count)]
for i, direcs in enumerate(chunks1):
    print(len(direcs))
    direcGen.job_script("slurm{}.fric".format(i),direcs,jobname="Si_highT{}".format(i))
