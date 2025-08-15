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
parser.add_argument("-nc", "--number_of_cuts", type=int, help="Number of cuts", required=True)

args, leftovers = parser.parse_known_args()

prm = args.parameter_file
output_path   = args.output_folder
number_of_cuts = args.number_of_cuts
input_path = prm.split(".")[0]

print(f"\n\nStarting postprocessing \n\n")
# Variables from the first section of the .prm file
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

# Particle size distribution
input_string = particle.prm_dict["custom diameters"]
# Split input string by commas and convert to float without adding a small value
list_of_diameter = input_string.split(',')
list_of_diameter = np.array([float(item) for item in list_of_diameter])

input_string = particle.prm_dict["custom volume fractions"]
list_of_volume_fraction = input_string.split(',')
list_of_volume_fraction = np.array([float(item) for item in list_of_volume_fraction])

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

print(f" ####### Lists of analysed vtus :"
      f"\n VTU measures :{vtu_measure}"
      f"\n #######")

# Constant used for the volume calculation
volume_cst = 1. / 6. * np.pi

# Create a container that will contain the volume fractions for each layer and each section in that layer. (3d array)
volume_fractions_each_section_all_layer       = np.zeros((len(vtu_measure),number_of_cuts, len(list_of_diameter)))
rel_density_each_section_all_layer            = np.zeros((len(vtu_measure),number_of_cuts))
cumulative_rel_density_each_section_all_layer = np.zeros((len(vtu_measure),number_of_cuts))

# Volume on the build plate for each section for each layer. 
volume_on_BP_each_layer_each_section = np.zeros((len(vtu_measure),number_of_cuts))

# Loop over every vtu to measure. The the particles that are on the build plate.
for index, k in enumerate(vtu_measure):
    # Load the position in df
    temp_df = particle.get_df(k)
        
    # Create a panda date frame (df)
    # Pyvista data frame are a bit weird... the conditions used in this code
    # to isolate the particle located over the build plate are not working with
    # them. Because of this, I'm transfering the required data into a panda data frame
    # and then use it to filter the particles.
    df = pd.DataFrame(temp_df.points, columns=['x', 'y', 'z'])
    df['diameter'] = temp_df['diameter']
    df.drop(['y', 'z'], axis=1) # We don't care about the y and z
    
    # Filter the particles that are on the build plate
    condition = (x_min_BP <= df['x']) & (df['x'] <= x_max_BP)
    df        = df[condition]
    
    ## Create the containers 
    # Volume of associated with each diameter value for each section for this layer. 
    volume_fractions_each_section = np.zeros((number_of_cuts, len(list_of_diameter)))
    
    # Relative density for each section.
    rel_density_each_section            = np.zeros(number_of_cuts) 
    cumulative_rel_density_each_section = np.zeros(number_of_cuts) 
    
    # Loop over every section
    for v in range(number_of_cuts):
        
        #%% Particle size distribution 
        # beginning of the section
        x_min = x_min_BP + v * (build_plate_length / number_of_cuts)
        
        # end of the section
        x_max = x_min_BP + (v + 1) * (build_plate_length / number_of_cuts)
        
        # Find the number of particles with each diameter value in the current section.
        condition   = (x_min <= df['x']) & (df['x'] <= x_max)
        df_filtered = df[condition]
        
        # Find the number of particles with each diameter value in the current section.
        diameters                = df_filtered["diameter"].to_numpy()
        unique_diameters, counts = np.unique(diameters, return_counts=True)
        
        # Volume associated with each diameter value in the current section.
        volume_each_diameter = volume_cst * counts * (unique_diameters ** 3)  # Volume of each diameter
        
        # Total volume in the current section
        total_volume_section = np.sum(volume_each_diameter)
        
        # Volume fraction of each diameter in the current section
        volume_fractions_each_section[v:] = volume_each_diameter / total_volume_section  # Volume fraction of each diameter       
        
        #%% Local relative density 
        diameters = df_filtered["diameter"].to_numpy()
        volume_on_BP_each_layer_each_section[index,v] = volume_cst * np.sum(diameters ** 3)

        if index == 0:
            continue
        
        # Total vertical displacement of the build plate
        total_height                  = (index - 1) * delta_n
        available_volume_this_section = total_height * build_plate_area / number_of_cuts
        this_layer_height             = delta_n
        
        # If the current layer is 0, the effective layer height is delta_o + delta_n
        if index == 0:
            this_layer_height          += delta_o
            rel_density_each_section[v] = (volume_on_BP_each_layer_each_section[index,v]) / (this_layer_height * build_plate_area / number_of_cuts)
        
        else:
            rel_density_each_section[v] = (volume_on_BP_each_layer_each_section[index,v] 
                                           - volume_on_BP_each_layer_each_section[index - 1,v]) / (this_layer_height * build_plate_area / number_of_cuts)

        # We start measuring the cumulative relative density from layer 1
        if index ==1:
            continue 
        
        cumulative_rel_density_each_section[v] =  (volume_on_BP_each_layer_each_section[index,v] - volume_on_BP_each_layer_each_section[1,v]) / available_volume_this_section
      
            
    volume_fractions_each_section_all_layer[index,:,:]     = volume_fractions_each_section      
    rel_density_each_section_all_layer[index,:]            = rel_density_each_section
    cumulative_rel_density_each_section_all_layer[index,:] = cumulative_rel_density_each_section
    

# save the container with the volume fractions for each layer and each section in that layer.
binary_dir = "./00_binary"
if not os.path.exists(binary_dir):
    os.makedirs(binary_dir)

print(volume_fractions_each_section_all_layer)

np.save(output_path + input_path + "_volume_fractions_all_layers", volume_fractions_each_section_all_layer)
# Save the list of diameter and original volume fractions
np.save(output_path + input_path + "_list_of_diameters", list_of_diameter)
np.save(output_path + input_path + "_list_of_volume_fraction", list_of_volume_fraction)
np.save(output_path + "number_of_cuts", number_of_cuts)

np.save(output_path + input_path + "_LRD_seg", rel_density_each_section_all_layer)
np.save(output_path + input_path + "_CRD_seg", cumulative_rel_density_each_section_all_layer)
np.save(output_path + input_path + "_number_of_layers", number_of_layers - 1)



print("Binary files saved!")
print("Job is done")
