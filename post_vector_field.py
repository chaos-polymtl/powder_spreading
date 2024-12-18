#############################################################################
"""
Postprocessing automation tool.

By: Olivier Gaboriault
Date: January 13th, 2024
"""
#############################################################################
'''Importing Libraries'''
import sys

import numpy as np
import bisect
import pandas as pd
import matplotlib.pyplot as plt
import pickle

from lethe_pyvista_tools import *

#############################################################################

# Take case path as argument
prm_file_names = np.array(
    [
        "25_03_200/25_03_200.prm",  # , Narval
        "50_03_200/50_03_200.prm",  # , Narval
    ])

for i in range(len(prm_file_names)):
    print(f"\n\n Starting postprocessing for simulation number {i + 1} / {len(prm_file_names)}.")
    # Variables from the first section of the .prm of the .prm file
    with open("./" + prm_file_names[i], 'r') as file:
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
    prm_file_name = (prm_file_names[i]).split('/')[1]

    pvd_name = 'out.pvd'
    ignore_data = ['type', 'volumetric contribution', 'velocity', 'torque', 'fem_torque', 'fem_force']
    particle = lethe_pyvista_tools((prm_file_names[i]).split('/')[0], prm_file_name, pvd_name, ignore_data=ignore_data)
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

    # Finding the departure time of all the blades
    plates_speed = 0.002
    plate_displacement_time = delta_n / plates_speed
    every_starting_time = np.empty(number_of_layers)
    every_starting_time[0] = first_starting_time
    for j in range(1, number_of_layers):
        every_starting_time[j] = every_starting_time[j - 1] + time_per_layer * delta_starting_time

    # Time step to measure the relative density off the powder on the build plate
    measuring_time_PB_segregation = every_starting_time + 0.87 * blade_time_per_layer

    vtu_measure = np.array([], dtype=int)

    # Loop over the vtu in the list and add the one right after the blade
    which_layer = 0
    index_F_RD = 0
    time = particle.time_list

    for j in range(len(particle.list_vtu)):
        if time[j] >= measuring_time_PB_segregation[which_layer]:
            vtu_measure = np.append(vtu_measure, int(j))
            which_layer += 1
            if which_layer == number_of_layers:
                break

    # Loop over this new list
    print(f" ####### Lists of analysed vtus :"
          f"\n VTU measure     :{vtu_measure}"
          f"\n #######")
    # Constant used for the volume calculation
    volume_cst = 1. / 6. * np.pi

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
    df_0_filtered = pd.DataFrame(particle_points, columns=['x', 'y', 'z'])
    df_0_filtered['ID'] = particle_ids
    condition = (df_0_filtered['x'] >= x_min_BP) & (df_0_filtered['x'] <= x_max_BP)
    df_0_filtered_filtered = df_0_filtered[condition]

    for index, k in enumerate(vtu_measure[1:]):
        print(f"Layer {index + 1}:")

        if index == 0:
            delta = delta_o
        else:
            delta = delta_n

        # Load the positions and IDs in df_0
        df_1 = particle.get_df(k)
        particle_points = df_1.points
        particle_ids = df_1["ID"][:]
        df_1_filtered = pd.DataFrame(particle_points, columns=['x', 'y', 'z'])
        df_1_filtered['ID'] = particle_ids

        condition = (df_1_filtered['x'] >= x_min_BP) & (df_1_filtered['x'] <= x_max_BP) & (
                df_1_filtered['z'] <= (0.05 * domain_z_length))
        df_1_filtered_filtered = df_1_filtered[condition]

        delta_df = []
        delta_df = pd.merge(df_0_filtered_filtered, df_1_filtered_filtered, on='ID', suffixes=('_t0', '_t1'))
        delta_df['dx'] = delta_df['x_t1'] - delta_df['x_t0']
        delta_df['dy'] = delta_df['y_t1'] - delta_df['y_t0'] + delta
        delta_df.drop(['z_t0', 'x_t1', 'y_t1', 'z_t1'], axis=1, inplace=True)
        dataframe_list.append(delta_df)
        df_0_filtered_filtered = df_1_filtered_filtered.copy()

    with open("./00_binary/" + prm_file_name.split(".")[0] + "_VECTOR_FIELD", 'wb') as file:
        pickle.dump(dataframe_list, file)
    print("Binary files saved!")
print("Job is done")
