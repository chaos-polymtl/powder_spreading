#############################################################################
"""
Postprocessing graph tool.

By: Olivier Gaboriault
Date: December 19th, 2024
"""
#############################################################################
'''Importing Libraries'''
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#############################################################################
color_palette = np.array(["#fa8738ff","#728dc0ff",'#bfd3e6','#88419d','#810f7c','#4d004b',"black"])

# Name of the binary
prm_file_names   = ["25_03_200"]
labels = ["Test1","Test2","Test3","Test4"]

plt.figure(figsize=(10, 6))

parser = argparse.ArgumentParser(description='Arguments for the generation of graphs about the relative density over the build plate')
parser.add_argument("-exp_data", "--exprimental_data", type=str, help="Experimental data file path", required=False)
parser.add_argument("-plt_exp", "--plot_experimal_data", type=bool, help="Bool is your want to plot the experimental data", required=False, default=True)
parser.add_argument("-prm", "--parameter_files", type=str, help="Parameter files list ", required=True)
parser.add_argument("-if", "--input_folder", type=str, help="Input folder path where the binaries are stored",
                    required=False, default = "./00_binary/" )

args, leftovers = parser.parse_known_args()

plot_experimental_date   = args.plot_experimal_data # By default this is true 
if plot_experimental_date:
    exp_data_path = args.exprimental_data
    layer_number, R1, R2, R3 = np.loadtxt(exp_data_path, skiprows=1, unpack=True)
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

    plt.plot(layer_number, exp_cummulative, "--",
             label=r"Experimental - CRD", color="black",linewidth=2)

    plt.errorbar(layer_number, exp_avg, yerr=exp_error, fmt="-s", color="black",
                 label=r"Experimental - LRD", markersize=5, capsize=5)


# Loop over the list of files provided
binary_folder = args.input_folder

print(prm_file_names)
for index, i in enumerate(prm_file_names):

    prefix = i
    CRD = np.load(binary_folder + prefix + '_CRD.npy')
    LRD = np.load(binary_folder + prefix + '_LRD.npy')
    NLayer = np.load(binary_folder + prefix + '_number_of_layers.npy')
    print(NLayer)
    print(LRD)

    plt.plot(np.arange(NLayer-1), LRD[1:], "-x", label=labels[index] + "- LRD", color=color_palette[index], linewidth=2)

    plt.plot(np.arange(NLayer-1), CRD[1:], "--", label=labels[index] + "- CRD", color=color_palette[index], linewidth=2)

plt.xlabel("Layer number", fontsize=24)
plt.ylabel("Relative density ", fontsize=24)
plt.locator_params(axis='x', integer=True)
plt.xticks(np.arange(0, 21))
plt.ylim(0.51, 0.69)
plt.legend(loc='lower right', fontsize=15, ncol=2)
plt.subplots_adjust(left=0.11, right=0.99, top=0.98, bottom=0.12)
plt.tick_params(axis='both', which='major', labelsize=18)
plt.savefig('./00_figures/' + "results" + '.png')

#plt.show()

print("Job is done")
