#############################################################################
"""
Postprocessing automation tool.

By: Olivier Gaboriault
Date: December 10th, 2024
"""

#############################################################################
# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lethe_pyvista_tools import *

#############################################################################

# Parameter file paths
prm_file_names = np.array(
    [
        "25_03_200/25_03_200.prm",
        "50_03_200/50_03_200.prm",
    ])
radius_multiplier = 4.
step_size = 1.

# Loop over all prm files
for i in range(len(prm_file_names)):
    print(
        f"\n\n Starting postprocessing for simulation number {i + 1} / {len(prm_file_names)}.")

    # Variables from the first section of the prm
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
    # extra_time_layer_zero = float((lines[14]).split('=')[1])
    blade_thickness = 0.004267766952966369

    # Create the particle object
    prm_file_name = prm_file_names[i].split('/')[1]
    path = prm_file_names[i].split('/')[0]
    pvd_name = 'out.pvd'
    ignore_data = ['type', 'volumetric contribution', 'velocity', 'torque',
                   'fem_torque', 'fem_force']
    particle = lethe_pyvista_tools(path, prm_file_name, pvd_name,
                                   ignore_data=ignore_data)
    #############################################################################

    d_max = float(particle.prm_dict["custom diameters"].split(",")[
                      -1])  # Maximum particle diameter
    distance_threshold = d_max * radius_multiplier  # Box size used to compute the local relative density

    # Build plate domain
    # This string is used to isolate the start and the end of the build plate
    input_string = particle.prm_dict["initial translation"]
    x_min_BP = float(input_string[2].split(',')[
                         0])  # This is the X translation of solid object #2
    x_max_BP = float(input_string[3].split(',')[
                         0])  # This is the X translation of solid object #3

    # Length of the domain
    input_string = particle.prm_dict["grid arguments"].split(',')
    domain_x_length = float(
        input_string[4].split(':')[1])  # This is the dealii triangulation in X
    domain_z_length = float(
        input_string[6].split(':')[0])  # This is the dealii triangulation in Z
    build_plate_length = x_max_BP - x_min_BP
    build_plate_area = domain_z_length * build_plate_length

    # How much time it takes for a blade to move through the domain :
    time_per_layer = (domain_x_length + blade_thickness) / blade_speed
    # This is used to find the starting time of each blade.
    # With this starting time, we can find all the measuring times.

    # Finding the departure time of all the blades (Measuring plate)
    plates_speed = 0.002  # Measuring plate average velocity
    every_starting_time = np.empty(number_of_layers)
    every_starting_time[0] = first_starting_time
    for j in range(1, number_of_layers):
        every_starting_time[j] = every_starting_time[
                                     j - 1] + time_per_layer * delta_starting_time

    # Time step to measure the relative density off the powder on the build plate
    # This parameter is arbitrarily. If the measurements are taken when the blade
    # is still on the BP, this number should be bigger.
    trigger_parameter = 0.86

    measuring_time_PB_rel_density = every_starting_time + trigger_parameter * time_per_layer

    # Create lists of vtus we want to analyse
    vtu_measure = np.array([], dtype=int)

    # Loop over the vtu time in the list and add the ones that are bigger than
    # the measuring time created earlier in this code.
    # In other words, we are creating the list of vtu that we will analyse.
    which_layer = 0
    time = particle.time_list

    for j in range(len(particle.list_vtu)):
        if time[j] >= measuring_time_PB_rel_density[which_layer]:
            vtu_measure = np.append(vtu_measure, int(j))
            which_layer += 1
            if which_layer == number_of_layers:
                break

    BP_rel_density_each_layer = np.array([])
    BP_rel_density_cumulative = np.array([])
    volume_on_BP = np.zeros(number_of_layers)

    # This list should be look at, just to be sure that the blade is pass the build plate.
    print(f" ####### Lists of analysed vtus :"
          f"\n Vtu measured :{vtu_measure}"
          f"\n #######")

    # Constant used for the volume calculation
    volume_cst = 1. / 6. * np.pi

    # Creating the measurement points
    # We add/subtract 0.5 * distance_threshold so that the edge of the zone are on the measuring plate.
    px_min = x_min_BP + 0.5 * distance_threshold
    px_max = x_max_BP - 0.5 * distance_threshold

    # Each calculation location are spaced by step_size * d_max
    location_x = np.arange(px_min, px_max, step_size * d_max)

    # For now, we are only interested in the last layer
    total_height = number_of_layers * delta_n
    location_y = np.arange(-total_height + 1. * distance_threshold,
                           0. - 0.5 * distance_threshold,
                           step_size * d_max, dtype=float)

    # Load the position and diameter of particles at the last measuring vtu.
    df_0 = particle.get_df(vtu_measure[-1],)

    # Create a panda date frame (df)
    # Pyvista data frame are a bit weird... the conditions used in this code
    # to isolate the particle located over the build plate are not working with
    # them. Because of this, I'm transferring the required data into a panda df
    df = pd.DataFrame(df_0.points, columns=['x', 'y', 'z'])
    df['diameter'] = df_0['diameter']
    df.drop(['z'], axis=1)
    condition = (x_min_BP <= df['x']) & (df['x'] <= x_max_BP)

    # Every particle in this data-frame are on the build-plate.
    df = df[condition]

    avail_vol = (
                            distance_threshold ** 2) * domain_z_length  # Volume available in the square.

    position = np.zeros(
        (len(location_y) * len(location_x), 2))  # Center of each square.
    rel_density = np.zeros(
        len(location_y) * len(location_x))  # Relative density values
    index = 0
    for px in location_x:
        x_min = px - 0.5 * distance_threshold  # x min of the square
        x_max = px + 0.5 * distance_threshold  # x max of the square

        condition = (x_min <= df['x']) & (df['x'] <= x_max)
        df_filtered = df[
            condition]  # We are only interested in the particle in those boundaries

        for py in location_y:
            position[index] = [px, py]
            y_min = py - 0.5 * distance_threshold  # y min of the square
            y_max = py + 0.5 * distance_threshold  # y max of the square
            condition = (y_min <= df_filtered['y']) & (
                    df_filtered['y'] <= y_max)

            df_filtered_twice = df_filtered[condition]  # Same thing, now in y

            # Compute the volume in the square
            volume_in_zone = np.sum(
                volume_cst * (df_filtered_twice["diameter"]) ** 3)
            rel_density[
                index] = volume_in_zone / avail_vol  # Compute the relative density
            index += 1

    x_positions = position[:,
                  0] - x_min_BP  # Extracting x coordinates, zeros is the beginning of the build-plate
    y_positions = position[:, 1]  # Extracting x coordinates

    # Just for visualization purposes, the shape of the relative density need to change.
    rotated_density = rel_density.reshape(len(location_x),
                                          len(location_y)).transpose()
    plt.imshow(rotated_density,
               extent=[x_positions[0], x_positions[-1], y_positions[0],
                       y_positions[-1]], origin='lower',
               cmap="Blues")  # interpolation='bilinear',

    plt.colorbar(label='Relative Density', orientation="horizontal")
    plt.title(r"$\rho_{rel}$ on the build plate")
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.tight_layout()  # Adjust layout to prevent cutoff
    plt.savefig("Result.svg")
    plt.show()

    print("Binary files saved!")

print("Job is done")
