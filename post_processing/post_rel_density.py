#############################################################################
"""
Postprocessing automation tool.

By: Olivier Gaboriault
Date: January 13th, 2024
"""
#############################################################################
'''Importing Libraries'''
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from lethe_pyvista_tools import *
from post_function import *

#############################################################################

parser = argparse.ArgumentParser(description='Arguments for calculation relative density over the build plate')
parser.add_argument("-of", "--output_folder", type=str, help="Output folder path", required=False, default = "./00_binary/" )
parser.add_argument("-prm", "--parameter_file", type=str, help="Parameter file", required=True)
args, leftovers = parser.parse_known_args()

prm = args.parameter_file
output_path   = args.output_folder

input_path = prm.split(".")[0]

print(f"\n\nStarting postprocessing \n\n")
# Variables from the first section of the .prm of the .prm file
with open("./" + input_path  + "/" + prm , 'r') as file:
    lines = file.readlines()  # Read all lines into a list

number_of_layers = int((lines[3]).split('=')[1]) + 2
blade_speed = float((lines[4]).split('=')[1])
delta_B_P = float((lines[5]).split('=')[1])
delta_o = float((lines[6]).split('=')[1])
delta_n = float((lines[7]).split('=')[1])
GAP = float((lines[9]).split('=')[1])
first_layer_extrusion = float((lines[10]).split('=')[1])
n_layer_extrusion = float((lines[11]).split('=')[1])
first_starting_time = float((lines[12]).split('=')[1])
delta_starting_time = float((lines[13]).split('=')[1])
blade_thickness = 0.004267766952966369


pvd_name = 'out.pvd'
ignore_data = ['type', 'volumetric contribution', 'velocity', 'torque', 'fem_torque', 'fem_force']
particle = lethe_pyvista_tools(input_path, prm, pvd_name, ignore_data=ignore_data)
#############################################################################

# Bluid plate domain
# This string could be use to isolate the start and the end of the build plate (not for now)
input_string = particle.prm_dict["initial translation"]
x_min_Feeder = float(input_string[0].split(',')[0])  # --> This is the X translation of solid object #1
x_max_Feeder = float(input_string[1].split(',')[0])  # --> This is the X translation of solid object #1
x_min_BP = float(input_string[2].split(',')[0])      # --> This is the X translation of solid object #2
x_max_BP = float(input_string[3].split(',')[0])      # --> This is the X translation of solid object #3

# Lenght of the domain
input_string = particle.prm_dict["grid arguments"].split(',')
domain_x_length = float(input_string[4].split(':')[1])  # This is the dealii triangulation in X
domain_z_length = float(input_string[6].split(':')[0])  # This is the dealii triangulation in Z
build_plate_length = x_max_BP - x_min_BP
build_plate_area = domain_z_length * build_plate_length

# Times it takes for a blade to cross the domain in the X direction
time_per_layer = (domain_x_length + blade_thickness) / blade_speed

# Finding the departure time of all the blades (Measuring plate)
plates_speed = 0.002
every_starting_time = starting_times(number_of_layers, delta_n, plates_speed,first_starting_time, delta_starting_time, time_per_layer)

# Time step to measure the relative density off the powder on the build plate
# This parameter is arbitrarily. If the measurements are taken when the blade
# is still on the BP, this number should be bigger.
trigger_parameter = 0.86
measuring_time = every_starting_time + trigger_parameter * time_per_layer

# Creating the list of vtu to analyze.
time = particle.time_list
vtu_measure = measuring_vtu_list(number_of_layers, time, measuring_time)

rel_density_each_layer = np.zeros(len(vtu_measure)) # Array for the layer relative density 
rel_density_cumulative = np.zeros(len(vtu_measure)) # Array for the layer cummulative density 
volume_on_BP           = np.zeros(len(vtu_measure))

print(f" ####### Lists of analysed vtus :"
      f"\n BP_rel_density     :{vtu_measure}"
      f"\n #######")

# Constant used for the volume calculation
volume_cst = 1. / 6. * np.pi

for index, k in enumerate(vtu_measure):
    # Load the position in df
    df_0 = particle.get_df(k)
    
    # Create a panda date frame (df)
    # Pyvista data frame are a bit weird... the conditions used in this code
    # to isolate the particle located over the build plate are not working with
    # them. Because of this, I'm transfering the required data into a panda df
    df = pd.DataFrame(df_0.points, columns=['x', 'y', 'z'])
    df['diameter'] = df_0['diameter']
    df.drop(['y', 'z'], axis=1) # We don't care about the y and z direction for now 

    condition = (x_min_BP <= df['x']) & (df['x'] <= x_max_BP)

    # Every particles in this data-frame are on the build-plate.
    df_filtered = df[condition]
    volume_on_BP[index] = np.sum(volume_cst * (df_filtered["diameter"]) ** 3) # Sum of all the individual volumes
    
    if index != 0: # We don't compute the relative density of the first layer. (Doing the same thing as the experiments)
        # Total vertical displacement of the build plate
        total_height = index * delta_n
        available_volume = total_height * build_plate_area
        this_layer_height = delta_n
        rel_density_cumulative[index] =  (volume_on_BP[index] - volume_on_BP[0]) / available_volume
        rel_density_each_layer[index] = (volume_on_BP[index] - volume_on_BP[index - 1]) / (this_layer_height * build_plate_area)


print(f" Powder volume on build plate      : \n{volume_on_BP} \n ######## ")
print(f" Relative density of each layer    : \n{rel_density_each_layer} \n ######## ")
print(f" Cummulative relative density      : \n{rel_density_cumulative} \n ########")

binary_dir = "./00_binary"
if not os.path.exists(binary_dir):
    os.makedirs(binary_dir)

np.save(output_path + input_path + "_LRD", rel_density_each_layer)
np.save(output_path + input_path + "_CRD", rel_density_cumulative)
np.save(output_path + input_path + "_number_of_layers", number_of_layers - 1)

print("Binary files saved!")
print("Job is done")
