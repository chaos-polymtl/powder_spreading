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
import pickle

from lethe_pyvista_tools import *
from post_function import *

#############################################################################
parser = argparse.ArgumentParser(description='Arguments for calculation relative density over the build plate')
parser.add_argument("-of", "--output_folder", type=str, help="Output folder path", required=False, default = "./00_binary/" )
parser.add_argument("-i", "--input", type=str, help="Parameter file", required=True)
args, leftovers = parser.parse_known_args()

prm_path = args.input
output_path   = args.output_folder

print(f"\n\n Starting postprocessing.")
# Variables from the first section of the .prm of the .prm file
with open("./" + prm_path, 'r') as file:
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

# Create the particle object
path = prm_path.split('/')[0]
prm_file_name = prm_path.split('/')[-1]

pvd_name = 'out.pvd'
ignore_data = ['type', 'volumetric contribution', 'velocity', 'torque', 'fem_torque', 'fem_force']
particle = lethe_pyvista_tools(path, prm_file_name, pvd_name, ignore_data=ignore_data)
#############################################################################

# Bluid plate domain
# This string could be use to isolate the start and the end of the build plate (not for now)
input_string = particle.prm_dict["initial translation"]
x_min_Feeder = float(input_string[0].split(',')[0])  # --> This is the X translation of solid object #1
x_max_Feeder = float(input_string[1].split(',')[0])  # --> This is the X translation of solid object #1
x_min_BP = float(input_string[2].split(',')[0])  # --> This is the X translation of solid object #2
x_max_BP = float(input_string[3].split(',')[0])  # --> This is the X translation of solid object #3

# Lenght of the domain
input_string = particle.prm_dict["grid arguments"].split(',')
domain_x_length = float(input_string[4].split(':')[1])  # This is the dealii triangulation in X
domain_z_length = float(input_string[6].split(':')[0])  # This is the dealii triangulation in Z
build_plate_length = x_max_BP - x_min_BP
build_plate_area = domain_z_length * build_plate_length

# How much time it takes for a blade to move throw all the domain
# This will help to find the starting time of each blade, thus the measuring time we should use
blade_time_per_layer = domain_x_length / blade_speed

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

print(f" ####### Lists of analysed vtus :"
      f"\n VTU measure     :{vtu_measure}"
      f"\n #######")
    
# Particle age dictiory. We use two dict, this way we don't need to check the particle ID that have just been added.
# We check in the old dict, then we merge the two dict at the end.
particle_id_on_build_plate = np.array([])
list_of_displacement_vectors_per_layer = {}
id_to_position = {}

# We go in reverse so that we don't need to check if the particle was on the build plate on the previous layers
dataframe_list = []

# Load the positions and IDs in df_0
df_0 = particle.get_df(vtu_measure[0])
particle_points = df_0.points
particle_ids = df_0["ID"][:]

# Create a panda date frame (df)
# Pyvista data frame are a bit weird... the conditions used in this code
# to isolate the particle located over the build plate are not working with
# them. Because of this, I'm transfering the required data into a panda df
df_0_filtered = pd.DataFrame(particle_points, columns=['x', 'y', 'z'])
df_0_filtered['ID'] = particle_ids
    

condition = (df_0_filtered['x'] >= x_min_BP) & (df_0_filtered['x'] <= x_max_BP)
    
# Every particles in this data-frame are on the build-plate
df_0_filtered_filtered = df_0_filtered[condition]

    # Start the loop
for index, k in enumerate(vtu_measure[1:]):
    print(f"Layer {index + 1}:")
    delta = delta_n

    # Load the positions and IDs in df_0
    df_1 = particle.get_df(k)
    particle_points = df_1.points
    particle_ids = df_1["ID"][:]

    # Create a panda date frame (df)
    df_1_filtered = pd.DataFrame(particle_points, columns=['x', 'y', 'z'])
    df_1_filtered['ID'] = particle_ids

    condition = (df_1_filtered['x'] >= x_min_BP) & (df_1_filtered['x'] <= x_max_BP) & (
        df_1_filtered['z'] <= (0.05 * domain_z_length)) # 0.05 is to have less arrows on the graph, otherwise, we don't see well what is going on.
    df_1_filtered_filtered = df_1_filtered[condition]

    delta_df = [] # Create/Clear the df
        # Merge both data frame using the particle ID 
    delta_df = pd.merge(df_0_filtered_filtered, df_1_filtered_filtered, on='ID', suffixes=('_t0', '_t1'))
    delta_df['dx'] = delta_df['x_t1'] - delta_df['x_t0']
    delta_df['dy'] = delta_df['y_t1'] - delta_df['y_t0'] + delta

    # Drop what is not usefull
    delta_df.drop(['z_t0', 'x_t1', 'y_t1', 'z_t1'], axis=1, inplace=True)
    dataframe_list.append(delta_df)
    
    df_0_filtered_filtered = df_1_filtered_filtered.copy()

with open("./00_binary/" + prm_file_name.split(".")[0] + "_VECTOR_FIELD", 'wb') as file:
    pickle.dump(dataframe_list, file)

np.save(output_path + prm_file_name.split(".")[0] + "_number_of_layers", number_of_layers - 1)

print("Binary files saved!")
print("Job is done")
