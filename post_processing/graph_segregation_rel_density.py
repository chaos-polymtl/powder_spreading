#############################################################################
"""
Postprocessing graph tool.

By: Olivier Gaboriault
Date: December 19th, 2024
"""
#############################################################################
'''Importing Libraries'''
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#############################################################################
# Create a 8 color colorpalette

color_palette = np.array(['#e41a1c','#377eb8','#4daf4a',
                           '#984ea3','#ff7f00',
                           '#a65628','#f781bf','#999999'])

markers_palette = np.array(['o', 's', '^', 'v', 'D', 'X', 'H', 'P'])

# Name of the binary
prm_file_names   = ["20_10_350", "20_20_250", "40_35_80"]
L = "L4"
labels = ["PS1-", "PS2-", "PS3-"]

plot_experimental_data  = True
binary_folder = "./00_binary/"

n_cuts = np.load(binary_folder + 'number_of_cuts.npy')

for index, i in enumerate(prm_file_names):
    prefix = i
    cumu_rel_density = np.load(binary_folder + prefix + '_CRD_seg.npy')

    rel_density      = np.load(binary_folder + prefix + '_LRD_seg.npy')

    for j in range(n_cuts):
        cumu_rel_density_this_section = cumu_rel_density[:, j]
        rel_density_this_section      = rel_density[:, j]
        
        plt.figure(figsize=(12, 6), constrained_layout=True)
        
        plt.plot(np.arange(1,len(rel_density_this_section )) , rel_density_this_section[1:], "-x", label=labels[index] + " - LRD", color=color_palette[index], linewidth=2)

        plt.plot(np.arange(2,len(rel_density_this_section )), cumu_rel_density_this_section[2:], "--", label=labels[index] + " - CRD", color=color_palette[index], linewidth=2)
        
        
        plt.xlabel("Layer number", fontsize=24)
        plt.ylabel("Relative density ", fontsize=24)
        plt.locator_params(axis='x', integer=True)
        plt.xticks(np.arange(0, 21))
        plt.ylim(0.52, 0.71)
        plt.legend(loc='lower right', fontsize=15, ncol=2)
        plt.subplots_adjust(left=0.13, right=0.99, top=0.98, bottom=0.12)
        plt.tick_params(axis='both', which='major', labelsize=18)
        
        plt.show()

    
#figures_dir = "./00_figures"
#if not os.path.exists(figures_dir):
#    os.makedirs(figures_dir)


#plt.savefig('./00_figures/' + "segregation" + '.png', dpi=500)

#plt.show()

print("Job is done")
