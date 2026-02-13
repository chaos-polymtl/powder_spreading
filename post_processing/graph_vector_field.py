#############################################################################
"""
Postprocessing automation tool.

By: Olivier Gaboriault
Date: January 13th, 2024
"""
#############################################################################
'''Importing Libraries'''
import sys as os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle


from lethe_pyvista_tools import *

#############################################################################
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['figure.figsize'] = (10,8)
plt.rcParams['lines.linewidth'] = 4
plt.rcParams['lines.markersize'] = '11'
plt.rcParams['markers.fillstyle'] = "none"
plt.rcParams['lines.markeredgewidth'] = 2
plt.rcParams['legend.columnspacing'] = 2
plt.rcParams['legend.handlelength'] = 3
plt.rcParams['legend.handletextpad'] = 0.2
plt.rcParams['legend.frameon'] = True
plt.rcParams['legend.fancybox'] = False
plt.rcParams['xtick.major.width'] = 2
plt.rcParams['xtick.major.size'] = 5
plt.rcParams['ytick.major.size'] = 5
plt.rcParams['ytick.major.width'] = 2
plt.rcParams['font.size'] = '25'
plt.rcParams['font.family']='DejaVu Serif'
plt.rcParams['font.serif']='cm'
plt.rcParams['savefig.bbox']='tight'
plt.rcParams['legend.handlelength']=1

# Take case path as argument
prm_file_names   = ["D", "E", "F", "G","H", "I"]#, "20_20_250", "40_35_80"
labels = ["D", "E", "F", "G","H", "I"]

start_measuring_plate = 0.03621428571428571

color_palette = np.array(['#bfd3e6', '#9ebcda', '#8c96c6', '#8c6bb1', '#88419d', '#810f7c', '#4d004b', 'black', "red"])
# Loop over the prm files
for i in range(len(prm_file_names)):
    prefix = prm_file_names[i].split('/')[-1].split('.')[0]

    # DISP_VECT == Displacement vector
    with open('./00_binary/' + prefix + '_VECTOR_FIELD', 'rb') as file:
        VectorFields = pickle.load(file)

    #print(VectorFields)

    NLayer = np.load('./00_binary/' + prefix + '_number_of_layers.npy')
    for j in range(len(VectorFields)):
        V_field = VectorFields[j]
        print(f"Layer {j+1} of {NLayer} | {prefix}")
        
        z = V_field['z_t0']
        condition = (z < 0.00004)
        V_field = V_field[condition]
        
        start_x = V_field['x_t0'] - start_measuring_plate
        start_y = V_field['y_t0']
        dx = 0.1 * V_field['dx']
        dy = 0.1 * V_field['dy']        

        threshold = 2e-6
        colors = 'black'# ['tab:blue' if d > threshold else 'tab:red' if d < -threshold else 'black'for d in dy]

        plt.figure(figsize=(10, 6))
        plt.quiver(start_x, start_y, dx, dy, scale_units='xy', scale=1, color=colors)

        #plt.ylim(-0.0014, 0.0002)
        #plt.xlim(0.0345, 0.0565)
        plt.title(f"Layer {j+1}",pad=10)        #plt.title("Displacement field: " + labels[i] + f" | Layer {j+1}", pad=10)
        plt.xlabel('x')
        plt.ylabel('y')
        #plt.xlim(0,0.02)
        y_min = -0.0022
        plt.ylim(y_min,0.0002)
        
        
        x_max = 0.057071 - start_measuring_plate
        plate_y = -100e-6 * (j + 1) - 10e-6
        y_array = np.array([plate_y, plate_y])
        x_array = np.array([0, x_max])
        
        
        x1_array = np.array([0,0])
        x2_array = np.array([x_max,x_max])
        y1_array = np.array([y_min, 0])
        
        
        #plt.plot(x1_array, y1_array, color='black', linewidth=2, linestyle='-')
        #plt.plot(x2_array, y1_array, color='black', linewidth=2, linestyle='-')
        #plt.plot(x_array , y_array, color='black', linewidth=2, linestyle='-')
        
         
        plt.subplots_adjust(left=0.05, right=0.99, top=1., bottom=0.1)

        figures_dir = "./00_figures"
        if not os.path.exists(figures_dir):
            os.makedirs(figures_dir)

        plt.savefig('./00_figures/' + prefix + f"_vector_field_{j+1:02d}" + '.pdf',dpi=500)
        plt.savefig('./00_figures/0_' + prefix + f"_vector_field_{j+1:02d}" + '.png',dpi=500)
        #plt.show()
        plt.close()


print("Job is done")
