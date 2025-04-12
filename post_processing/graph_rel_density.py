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
prm_file_names   = ["20_20_250", "20_10_350", "40_35_80"]
labels = ["20_20_250", "20_10_350", "40_35_80"]

plot_experimental_data  = True
exp_data_path = "/home/gabo/work/lethe/powder_spreading/experimental.data"
binary_folder = "./00_binary/"

plt.figure(figsize=(10, 6))

def effective_rel_den_to_cummu(eff_rel_density):
    
    cummulative_density = np.zeros_like(eff_rel_density)
    for i in range(len(eff_rel_density)):
        cummulative_density[i] = np.sum(eff_rel_density[:(i + 1)]) / (i + 1)
    
    return cummulative_density

if plot_experimental_data:
    layer_number, R1_temp, R2_temp, R3_temp = np.loadtxt(exp_data_path, skiprows=1, unpack=True)
    
    
    CR1 = effective_rel_den_to_cummu(R1_temp)
    CR2 = effective_rel_den_to_cummu(R2_temp)
    CR3 = effective_rel_den_to_cummu(R3_temp)
    
    R1 = R1_temp[1:]
    R1[0] = CR1[1] 
    
    R2 = R2_temp[1:]
    R2[0] = CR2[1] 
     
    R3 = R3_temp[1:] 
    R3[0] = CR3[1] 
    
    exp_avg = (R1 + R2 + R3) / 3
    
    # Experimental cummulative relative density 
    exp_cummulative = np.zeros_like(exp_avg)
    for i in range(len(exp_avg)):
        exp_cummulative[i] = np.sum(exp_avg[:(i + 1)]) / (i + 1)

    # Experimental min/max
    exp_min = np.minimum.reduce([R1,R2,R3])
    exp_max = np.maximum.reduce([R1,R2,R3])

    # Error bars 
    exp_error = [exp_avg - exp_min,  exp_max-exp_avg]

    plt.plot(layer_number[1:], exp_cummulative, "--",
             label=r"Experimental - CRD", color="black",linewidth=2)

    plt.errorbar(layer_number[1:], exp_avg, yerr=exp_error, fmt="-s", color="black",
                 label=r"Experimental - LRD", markersize=5, capsize=5)


for index, i in enumerate(prm_file_names):
        
    prefix = i
    CRD = np.load(binary_folder + prefix + '_CRD.npy')
    LRD = np.load(binary_folder + prefix + '_LRD.npy')
    
    #LRD    = LRD_t[1:]
    #LRD[0] = CRD[2]
    
    NLayer = np.load(binary_folder + prefix + '_number_of_layers.npy')
    

    plt.plot(np.arange(len(LRD)), LRD, "-x", label=labels[index] + "- LRD", color=color_palette[index], linewidth=2)

    plt.plot(np.arange(len(CRD)), CRD, "--", label=labels[index] + "- CRD", color=color_palette[index], linewidth=2)

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
