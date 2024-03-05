# working scoring technique to Track the thermodynamic phase changes 
#---Import OVITO modules---#
from ovito.io import *
from ovito.modifiers import *
from ovito.data import *
from ovito.vis import *

#---Import standard Python and NumPy modules---#
import os
import sys
import numpy as np
import math as m
from PyQt5 import QtCore
#import time


#begin = time.time()


################# load path ########################

_, filepath = sys.argv
#filepath = "/global/cfs/projectdirs/m3793/Arnab/Si_highT/50ns_run/5.05_1400/dump_5.05_1400" 


##################   Import file or file-sequence for number of frames ##############

pipeline = import_file('{}/System.*.LDA'.format(filepath))

#print(pipeline.source.num_frames)
frames = (pipeline.source.num_frames)
#print("total number of frames %i"%frames)


###################   Read the first frame for the total number of atoms   ##############

pipeline = import_file('{}/System.0.LDA'.format(filepath))


pipeline.modifiers.append(SelectExpressionModifier(expression = 'N'))

pipeline.compute()
Na = (np.count_nonzero(pipeline.output.particle_properties['Selection']))
#print("Total number of atoms = %i" %Na )




####################   Load the file-sequence for initial amorphous percentage   #### #######

pipeline = import_file('{}/System.*.LDA'.format(filepath))
pipeline.modifiers.append(IdentifyDiamondModifier(only_selected = False))
init_am = pipeline.compute(0)

Ia=(init_am.attributes["IdentifyDiamond.counts.OTHER"])


init_am_pct = (Ia/Na)*100

#print("initial amorphous percentage %f" %init_am_pct)

#######################  Loop over all the frames for average amorphous percentage  ##################

pipeline = import_file('{}/System.*.LDA'.format(filepath))
pipeline.modifiers.append(IdentifyDiamondModifier(only_selected = False))

am_data = []
for i in range(pipeline.source.num_frames):
    am = pipeline.compute(i)
    am_list = (am.attributes["IdentifyDiamond.counts.OTHER"])
    am_data.append(am_list)
am_arr = np.array(am_data)
am_arr_pct = (am_arr/Na)*100
am_deviation = np.std(am_arr_pct - init_am_pct)

#print(am_deviation)


max_am_data  = np.max(am_data)
#print("maximimum amorphous atoms in the trajectory = %i " %max_am_data)
min_am_data  = np.min(am_data)
#print("minimum amorphous atoms in the trajectory = %i" %min_am_data)


max_frac = (max_am_data/Na)*100
min_frac = (min_am_data/Na)*100
#print("maximum amorphous percentage in the traj = %f " %max_frac)
#print("minimum amorphous percentage in the traj = %f " %min_frac)

#######################   SCORE    #####################


#score = (avg_frac - init_am_pct)  # if amorphizing then the avg_am_frac > init_am_frac i.e, the score is +ve. else score is -ve
am_max_change = (max_frac - init_am_pct)
crys_max_change = (init_am_pct - min_frac)

#print("maximum change in amorphous from initial in the traj = %f" %am_max_change)
#print("maximum change in crystalline from initial in the traj = %f" %crys_max_change)

if (am_max_change) > (crys_max_change):
    score = (am_deviation *1)
elif(am_max_change) < (crys_max_change):
    score = (am_deviation *-1)
else:
    score =0


print(score)
