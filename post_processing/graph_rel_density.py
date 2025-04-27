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
color_palette = np.array(["#fa8738ff","#728dc0ff",'#bfd3e6','#88419d','#810f7c','#4d004b',"black"])

# Name of the binary
prm_file_names   = ["20_10_350", "20_20_250", "40_35_80"]
# prm_file_names   = ["20_10_350", "20_10_350_depth_x1" ]

labels = ["S1-L2-D2", "S1-L2-D1", "S3-L3"]

plot_experimental_data  = True
exp_data_path = "/home/gabo/work/lethe/powder_spreading/experimental.data"
binary_folder = "./00_binary/"

plt.figure(figsize=(10, 6))

def effective_rel_den_to_cumu(eff_rel_density):
    
    cumulative_density = np.zeros_like(eff_rel_density)
    for i in range(len(eff_rel_density)):
        cumulative_density[i] = np.sum(eff_rel_density[:(i + 1)]) / (i + 1)
    
    return cumulative_density

if plot_experimental_data:
    layer_number, R1, R2, R3 = np.loadtxt(exp_data_path, skiprows=1, unpack=True)
    
    exp_avg = (R1 + R2 + R3) / 3
    
    # Experimental cumulative relative density 
    exp_cumulative = np.zeros_like(exp_avg)
    for i in range(1,len(exp_avg)):
        exp_cumulative[i] = np.sum(exp_avg[1:i+1]) / (i)
        

    # Experimental min/max
    exp_min = np.minimum.reduce([R1,R2,R3])
    exp_max = np.maximum.reduce([R1,R2,R3])
    
    print("Layer 0, exp avg: ", exp_avg[0])
    print("Layer 0, exp min: ", exp_min[0])

    # Error bars 
    exp_error = [exp_avg - exp_min,  exp_max-exp_avg]

    plt.plot(layer_number[1:] + 1, exp_cumulative[1:], "--",
             label=r"Experimental - CRD", color="black",linewidth=2)

    plt.errorbar(layer_number + 1, exp_avg, yerr=exp_error, fmt="-s", color="black",
                 label=r"Experimental - LRD", markersize=5, capsize=5)


for index, i in enumerate(prm_file_names):
        
    prefix = i
    CRD = np.load(binary_folder + prefix + '_CRD.npy')
    LRD = np.load(binary_folder + prefix + '_LRD.npy')
    
    print()
    print(f"Layer 0, {labels[index]} - LRD      : ", LRD[1])
    print(f"Peak densification, {labels[index]} : ", np.max(LRD[2:]))
    print(f"Last layer, {labels[index]} - CRD   : ", CRD[-1])
    
        
    NLayer = np.load(binary_folder + prefix + '_number_of_layers.npy')
    
    plt.plot(np.arange(1,len(LRD)) , LRD[1:], "-x", label=labels[index] + " - LRD", color=color_palette[index], linewidth=2)

    plt.plot(np.arange(2,len(LRD)), CRD[2:], "--", label=labels[index] + " - CRD", color=color_palette[index], linewidth=2)

plt.xlabel("Layer number", fontsize=24)
plt.ylabel("Relative density ", fontsize=24)
plt.locator_params(axis='x', integer=True)
plt.xticks(np.arange(0, 21))
plt.ylim(0.51, 0.69)
plt.legend(loc='lower right', fontsize=15, ncol=2)
plt.subplots_adjust(left=0.11, right=0.99, top=0.98, bottom=0.12)
plt.tick_params(axis='both', which='major', labelsize=18)

figures_dir = "./00_figures"
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)


plt.savefig('./00_figures/' + "results" + '.png')

#plt.show()

print("Job is done")
