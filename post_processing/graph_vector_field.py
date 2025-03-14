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

# Take case path as argument
prm_file_names   = ["40_35_80", "20_10_350", "20_20_250"]
labels = ["40_35_80 ","20_10_350 ", "20_20_250 "]

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

        start_x = V_field['x_t0']
        start_y = V_field['y_t0']
        dx = 0.1 * V_field['dx']
        dy = 0.1 * V_field['dy']

        threshold = 2e-6
        colors = 'black'# ['tab:blue' if d > threshold else 'tab:red' if d < -threshold else 'black'for d in dy]

        plt.figure(figsize=(10, 6))
        plt.quiver(start_x, start_y, dx, dy, scale_units='xy', scale=1, color=colors)

        #plt.ylim(-0.0014, 0.0002)
        #plt.xlim(0.0345, 0.0565)
        plt.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.1)
        plt.title("Displacement field - " + prefix + f" - Layer {j+1}")
        plt.xlabel('x')
        plt.ylabel('y') 
        
        figures_dir = "./00_figures"
        if not os.path.exists(figures_dir):
            os.makedirs(figures_dir)

        plt.savefig('./00_figures/' + prefix + f"_vector_field_{j:02d}" + '.png',dpi=500)
        #plt.show()
        plt.close()


print("Job is done")
