"""
LPBF case generation automation tool.
By: Olivier Gaboriault
Date: February  16th, 2024
"""
import numpy as np
import jinja2
from gmsh_generator import *
from datetime import datetime
import os

from scipy.constants import precision

# Input parameters section :

# %% First input section. These parameters are general. They're the same as the parameters used in experimental part.
# These parameters will be written at the start of the prm file for the post-processing python code
id = "TI6AL4V-45-106"            # Used to identify the simulation in question in a specific parameter file.
blade_speed = 0.100              # Speed of the blades
number_of_layers = 20            # Number of layer. We do +2 in the code for layer -1 and 0.
delta_o = 100E-6                 # Thickness of the first layer
delta_n = 100E-6                 # Thickness of the following layers
first_layer_extrusion = 2200E-6  # Extrusion of the first layer
other_layer_extrusion = 600E-6   # Extrusion of the following layers
delta_b_p = 100E-6               # Distance between the tip of the blade and the transfert plate
delta_miss = 0.                  # Miss-match between the build-plate and the seperators
gap = 500E-6                     # Void around the build plate

# %% Second input section. These parameters are related to the simulation and are being 
# written at the start of the parameter file.
first_starting_time = 0.0  # Time at which the reservoir start to move for the first time.(s)
plates_speed = 0.002       # Vertical velocity (m/s)

# %% Third input section. These parameters are related to Solid object. Some are written at
# the beginning the parameter file.
solid_object_bool = "false"
blade_type = "R"  # R = round , F = Flat

# Related to round blade
blade_radius = 0.0025
blade_n_vertex = 50
blade_angle_ratio = 0.75

# Related to the flat blade
blade_thickness = 0.005

length_multiplier = 2
if length_multiplier == 1:
    subdivisions = "18,5,1"
    subdivisions_loading = "8,16,1"
    refinement   = "4"
    delta_starting_time = 0.70

elif length_multiplier == 2:
    subdivisions = "32,5,1"
    subdivisions_loading = "16,16,1"
    refinement = "4"
    delta_starting_time = 0.65
    
elif length_multiplier == 3:
    subdivisions = "48,6,1"
    subdivisions_loading = "24,16,1"
    refinement = "4"
    delta_starting_time = 0.65

reservoir_length = 0.01 * length_multiplier
separator_1_length = 0.0075 * length_multiplier # This includes the gap
gap_BP_distance = 100E-6

bp_length = 0.0105 * length_multiplier
separator_2_length = 0.0075 * length_multiplier
domain_dept = 0.0020

if blade_type == "R":
    blade_thickness = abs(blade_radius * (-1 + np.cos(0.75 * np.pi)))

domain_length = reservoir_length + separator_1_length + bp_length + 0.9 * separator_2_length

# %% Fourth input section. Related to the insertion and particles properties
distribution = "custom"  # "custom"
number_of_particles = 100_000_000

# Polydisperse parameters
# 10-90
diameter_values = np.array(
    [52.6220, 57.7666, 63.4141, 69.6138, 76.4196, 83.8907, 92.0923,
     101.0960]) * 1e-6
diameter_volume_fraction = np.array(
    [11.9540, 13.8083, 13.7866, 12.4325, 10.5924, 8.62023, 6.45482,
     4.13358]) / 100.
# Need to put back the volume fraction on 1.
diameter_volume_fraction = diameter_volume_fraction / np.sum(
    diameter_volume_fraction)

# Particles properties
young_particle = 105e9 / 4000
poisson_ratio_particles = 0.342
poisson_ratio_wall = poisson_ratio_particles
density_particle = 4386
G = young_particle / (2 * (1 + poisson_ratio_particles))
insertion_seed = 18

if distribution == "uniform":
    diameter_values = [np.max(diameter_values)]
    diameter_volume_fraction = [1.]

# Creating the string for the prm file related to the diameters.
# Formatting the diameter vectors into strings
formatted_diameter_values = ', '.join(
    format(x, '.10f') for x in diameter_values)
formatted_diameter_volume_fraction = ', '.join(
    format(x, '.5f') for x in diameter_volume_fraction)

# DEM time step
dem_time_step = 0.15 * (
        0.5 * np.pi * min(diameter_values) * np.sqrt(density_particle / G) * (
        1. / (0.1631 * poisson_ratio_particles + 0.8766)))
precision = 1e-12
dem_time_step = round(dem_time_step / precision) * precision

# Wall proprieties
young_wall = young_particle

# Initial translation in the x direction
blade_initial_x_translation = -0.0002
separator_1_x_translation = reservoir_length
bp_initial_x_translation = separator_1_x_translation + separator_1_length
separator_2_x_translation = bp_initial_x_translation + bp_length

# %% Reservoir and build plate displacement
# Time it takes for the plates to move for every new layers
plate_displacement_time = delta_n / plates_speed

# Times it takes for a blade to cross the domain in the X direction
time_per_layer = (domain_length + blade_thickness) / blade_speed

# Frequencies
delta_insert_time = delta_starting_time * time_per_layer
remove_box_x_max = 0.0142 * length_multiplier
insert_frequency = int(np.ceil(delta_insert_time / dem_time_step))
output_frequency = 90000

load_balancing_frequency = int(0.025 * insert_frequency + 1)
Restart_frequency = int(16. * load_balancing_frequency + 1)
print(Restart_frequency)

# Insertion files
insertion_files = "particles_00.input"
for it in range(1, number_of_layers + 1):
    insertion_files = insertion_files + f", particles_{it:02}.input"

# %% Generation the velocity functions for the blades
# Starts at 4, takes into account the feeder, the build plate and the two separators
solid_obj_id = 4
number_of_layers = number_of_layers + 1  # We add 2 for the layer #-1 and #0
total_solid_objects = 4 + number_of_layers

# Finding the departure time of all the blades
every_starting_time = np.empty(number_of_layers)
every_starting_time[0] = first_starting_time
for i in range(1, number_of_layers):
    every_starting_time[i] = every_starting_time[
                                 i - 1] + time_per_layer * delta_starting_time

# End of the simulation
end_time = (every_starting_time[-1] + time_per_layer + 0.01)

# Initializing the string
# First coater is for the leveling of the reservoir. The +0.02 is to make sure the blade exist the triangulation and
# doesn't block the particles in the following layer.
coater_function = f"if(t>= {every_starting_time[solid_obj_id - 4]:.5}, if(t<= {(every_starting_time[solid_obj_id - 4] + time_per_layer + 0.02):.5}, {blade_speed:.5}, 0), 0)"
all_coater = (f"    subsection solid object {solid_obj_id} \n"
              f"      subsection mesh \n"
              f"        set type                = gmsh \n"
              f"        set file name           = ./gmsh/Blade.msh\n"
              f"        set simplex             = true\n"
              f"        set initial refinement  = 0\n"
              f"        set initial translation = {blade_initial_x_translation}, {delta_b_p}, 0 \n"
              f"      end\n"
              f"      subsection translational velocity\n"
              f"        set Function expression = {coater_function}; 0; 0\n"
              f"      end\n"
              f"      set output solid object = {solid_object_bool}\n"
              f"    end\n")
solid_obj_id += 1

# This while loop is use to generate the translational velocity functions and to create
# the string that is going to be replacing the "Coaters" symbol in the parameter file.
while solid_obj_id - 4 < number_of_layers:
    end_time = (every_starting_time[solid_obj_id - 4] + time_per_layer + 0.01)
    coater_function = f"if(t>= {every_starting_time[solid_obj_id - 4]:.5}, if(t<= {(every_starting_time[solid_obj_id - 4] + time_per_layer + 0.02):.5}, {blade_speed:.5}, 0), 0)"

    coater_param = (f"   subsection solid object {str(solid_obj_id)} \n"
                    f"      subsection mesh \n"
                    f"         set type                = gmsh \n"
                    f"         set file name           = ./gmsh/Blade.msh\n"
                    f"         set simplex             = true\n"
                    f"         set initial refinement  = 0\n"
                    f"         set initial translation = {blade_initial_x_translation}, {delta_b_p}, 0\n"
                    f"      end\n"
                    f"      subsection translational velocity\n"
                    f"         set Function expression = {coater_function}; 0; 0\n"
                    f"      end\n"
                    f"   set output solid object = {solid_object_bool}\n"
                    f"   end\n")

    solid_obj_id += 1
    all_coater = all_coater + coater_param

# Here, we create the displacement function for the reservoir plate and build plate.
build_plate_func = str()

t3 = 0.
t4 = t3 + plate_displacement_time
const_first_layer_build_plate = delta_o / (
        (1. / 3.) * (t4 ** 3 - t3 ** 3) + 0.5 * (t3 + t4) * (
            t3 ** 2 - t4 ** 2) + (t3 * t4) * (t4 - t3))

build_plate_func = (
        build_plate_func + f"if(t>= {t3:.5}, if(t<= {t4:.5}, {-const_first_layer_build_plate:.5} * (t - {t3:.5}) "
                           f"* (t - {t4:.5}),")

# %% Other layers
for i in range(0, number_of_layers):
    t3 = every_starting_time[i] + (
            separator_2_x_translation + blade_thickness - blade_initial_x_translation) * 1.01 / blade_speed
    t4 = t3 + plate_displacement_time

    # This constant can be found by integrating the speed function we define. This speed function is a second degree
    # polynomial. The integral must be equal to the layer height
    const = delta_n / ((1 / 3) * (t4 ** 3 - t3 ** 3) + 0.5 * (t3 + t4) * (
                t3 ** 2 - t4 ** 2) + (t3 * t4) * (t4 - t3))

    # Concatenate the displacement functions for all the layers.
    build_plate_func = build_plate_func + f"if(t>= {t3:.5}, if(t<= {t4:.5}, {-const:.5} * (t - {t3:.5}) * (t - {t4:.5}),"

# Ending the functions
build_plate_func = build_plate_func + "0) "
for i in range(0, number_of_layers):
    build_plate_func = build_plate_func + ", 0) )"
build_plate_func = build_plate_func + ", 0)"

# Initial translation for the powder reservoir and domain lower limit in the Y direction.
initial_trans_reservoir = other_layer_extrusion * 3.
y_min = - max(np.abs(initial_trans_reservoir),
              np.abs(number_of_layers * delta_n + delta_o)) - 0.0005

# %% Jinja2
# Post_processing string for the post-processing python code
post_processing = (f"# This file was created on :  {datetime.now()}\n"
                   f"# ----- Post processing parameters ----- #\n"
                   f"# ID                      = {id}\n"
                   f"# Number of layers        = {number_of_layers - 1}\n"
                   f"# Blade speed             = {blade_speed:.5}\n"
                   f"# Delta_b_p               = {delta_b_p:.5}\n"
                   f"# Delta_0                 = {delta_o  :.5}\n"
                   f"# Delta_n                 = {delta_n  :.5}\n"
                   f"# Delta_miss_match        = {delta_miss:.5}\n"
                   f"# GAP                     = {gap:.5}\n"
                   f"# First layer extrusion   = {first_layer_extrusion:.5}\n"
                   f"# N layer extrusion       = {other_layer_extrusion:.5}\n"
                   f"# First starting time     = {first_starting_time} \n"
                   f"# Diff. between two blade = {delta_starting_time} \n"
                   f"# \n"  # f"# Extra time layer zero   = {extra_time_layer_zero}\n"
                   f"# Blade thickness         = {blade_thickness}\n"
                   f"#"
                   )
## File names ##
# Name of the .prm file created
CASE_PREFIX = f"{id}"

# Name of the output folder
output_folder = f"out_{id}_{datetime.now().date()}"

# Name of the restart files
restart_file = f"restart_{id}_{datetime.now().date()}"

# Name of the original .prm file being modified
PRM_FILE = 'template_spreading.prm'
PRM_FILE_LOADING = 'template_loading.prm'

PATH = os.getcwd()
templateLoader = jinja2.FileSystemLoader(searchpath=PATH)
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template(PRM_FILE)

# Replacing the symbols in the parameter file with the right expressions
output_text = template.render(Post_processing=post_processing,
                              Delta_t=str(dem_time_step),
                              End_time=end_time,
                              Log_freq=str(int(output_frequency/10)),
                              Output_freq=str(output_frequency),
                              Out=output_folder,
                              Restant_freq=str(Restart_frequency),
                              Restart_name=restart_file,
                              Load_Bal_freq=str(load_balancing_frequency),
                              Distribution=distribution,
                              Custom_diameters=formatted_diameter_values,
                              Custom_volume_fractions=formatted_diameter_volume_fraction,
                              Number_of_particles=str(number_of_particles),
                              Density=str(density_particle),
                              Young_particle=str(young_particle),
                              Poisson_particle=str(poisson_ratio_particles),
                              Young_wall=str(young_wall),
                              Poisson_wall=str(poisson_ratio_wall),
                              Trans_friction="{{Trans_friction}}",
                              Rolling_friction="{{Rolling_friction}}",
                              Surface_energy="{{Surface_energy}}",
                              Remove_box_x_max=remove_box_x_max,
                              Insert_files=insertion_files,
                              Insert_freq=str(insert_frequency),
                              Insert_box_z_max=f"{(domain_dept - 0.00005):.8}",
                              Seed=insertion_seed,
                              Subdivisions=subdivisions,
                              Y_min=f"{y_min:.5}",
                              X_max=f"{domain_length:.10}",
                              Z_max=domain_dept,
                              Refinement=refinement,
                              Reservoir_initial_translation=-initial_trans_reservoir,
                              Solid_object_bool=str(solid_object_bool),
                              Separator_1_init_trans=separator_1_x_translation,
                              Build_plate_init_trans=bp_initial_x_translation,
                              Build_plate_function=build_plate_func,
                              Separator_2_init_trans=f"{separator_2_x_translation:.5}",
                              Total_solid_objects=str(total_solid_objects),
                              Coaters=all_coater,
                              First_starting_time=str(first_starting_time)
                              )

prm_file_name = CASE_PREFIX + ".prm"
print(prm_file_name)
output_file_path = os.path.join("./", prm_file_name)
with open(output_file_path, 'w') as f:
    f.write(output_text)

#%% LOADING PRM
template = templateEnv.get_template(PRM_FILE_LOADING)

y_min_1 = - first_layer_extrusion - 3 * other_layer_extrusion
y_min_2 = -4 * other_layer_extrusion

for it in range(number_of_layers):
    if it == 0:
        initial_trans_reservoir = y_min_1
        # Time where the reservoir start moving
        t1 = 0.10 + (reservoir_length + blade_thickness + np.abs(
            blade_initial_x_translation)) * 1.01 / blade_speed
        # Time where it stop moving
        t2 = t1 + plate_displacement_time * 4.

        # This constant can be found when doing the integration of the velocity for a given displacement
        const = first_layer_extrusion / (
                (1 / 3) * (t2 ** 3 - t1 ** 3) + 0.5 * (t1 + t2) * (
                    t1 ** 2 - t2 ** 2) + (t1 * t2) * (t2 - t1))

        loading_reservoir_func = (
            f"if(t>= {t1:.5}, if(t<= {t2:.5}, {(const):.5} * "
            f"(t - {t1:.5}) * (t - {t2:.5}),0.),0)")
        coater_start_time = 0.10
        coater_end_time = (coater_start_time + (
                    bp_initial_x_translation + blade_thickness) / blade_speed + 0.02)
        loading_coater_func = (f"if(t>= {coater_start_time:.5}, "
                               f"if(t<= {coater_end_time:.5},"
                               f"{blade_speed:.5},0),0)")
        end_time = max(coater_end_time, t2) + 0.01
        number_of_particles = int(length_multiplier * 390_000)

    else:
        # Initial translation in y for the reservoir
        initial_trans_reservoir = y_min_2

        # Time where the reservoir start moving
        t1 = 0.1 + (reservoir_length + blade_thickness + np.abs(
            blade_initial_x_translation)) * 1.01 / blade_speed
        # Time where it stop moving
        t2 = t1 + plate_displacement_time

        # This constant can be found when doing the integration of the velocity for a given displacement
        const = other_layer_extrusion / (
                (1 / 3) * (t2 ** 3 - t1 ** 3) + 0.5 * (t1 + t2) * (
                    t1 ** 2 - t2 ** 2) + (t1 * t2) * (t2 - t1))

        loading_reservoir_func = (
            f"if(t>= {t1:.5}, if(t<= {t2:.5}, {(const):.5} * "
            f"(t - {t1:.5}) * (t - {t2:.5}),0.),0)")
        end_time = coater_end_time

        coater_start_time = 0.10
        coater_end_time = (coater_start_time + (
                    bp_initial_x_translation + blade_thickness) / blade_speed + 0.02)
        loading_coater_func = (f"if(t>= {coater_start_time:.5}, "
                               f"if(t<= {coater_end_time:.5},"
                               f"{blade_speed:.5},0),0)")
        end_time = max(coater_end_time, t2) + 0.25
        number_of_particles = int(length_multiplier * 225_000)

    # Replacing the symbols in the parameter file with the right expressions
    output_text = template.render(Post_processing=post_processing,
                                  Delta_t=str(dem_time_step),
                                  End_time=end_time,
                                  Log_freq=str(output_frequency),
                                  Output_freq=str(int(0.5 * output_frequency)),
                                  Out=output_folder + f"_{it}",
                                  Restant_freq=str(
                                      int(0.2 * Restart_frequency)),
                                  Restart_name=restart_file + f"_{it}",
                                  Load_Bal_freq=str(load_balancing_frequency),
                                  Distribution=distribution,
                                  Custom_diameters=formatted_diameter_values,
                                  Custom_volume_fractions=formatted_diameter_volume_fraction,
                                  Number_of_particles=str(number_of_particles),
                                  Density=str(density_particle),
                                  Young_particle=str(young_particle),
                                  Poisson_particle=str(poisson_ratio_particles),
                                  Young_wall=str(young_wall),
                                  Poisson_wall=str(poisson_ratio_wall),
                                  Trans_friction="{{Trans_friction}}",
                                  Rolling_friction="{{Rolling_friction}}",
                                  Surface_energy="{{Surface_energy}}",
                                  Insert_freq=str(insert_frequency),
                                  Insert_box_y_min=f"{(initial_trans_reservoir + 0.0005):.6f}",
                                  Insert_box_x_max=f"{(reservoir_length - 0.000001):.6f}",
                                  Insert_box_z_max=f"{(domain_dept - 0.00005):.6f}",
                                  Seed=insertion_seed,
                                  Subdivisions=subdivisions_loading,
                                  Y_min=f"{(initial_trans_reservoir - 0.0005):.6f}",
                                  X_max=f"{domain_length:.10}",
                                  Z_max=domain_dept,
                                  Refinement=refinement,
                                  Reservoir_initial_translation=initial_trans_reservoir,
                                  Reservoir_function=loading_reservoir_func,
                                  Solid_object_bool=str(solid_object_bool),
                                  Separator_1_init_trans=separator_1_x_translation,
                                  Build_plate_init_trans=bp_initial_x_translation,
                                  Delta_BP=delta_b_p,
                                  Coater_func=loading_coater_func)
    insertion_seed += 1
    prm_file_name_1 = CASE_PREFIX + f"_LOADING_{int(it)}.prm"
    output_file_path = os.path.join("./loading_prm/", prm_file_name_1)
    with open(output_file_path, 'w') as f:
        f.write(output_text)
        
    print(f"{prm_file_name_1} has been written.")
    
print(f"Writing the meshes\n")
if blade_type == "R":
    round_blade(blade_radius, blade_n_vertex, blade_angle_ratio, domain_dept)
else:  # Same thing for now since the flat plate function isn't created yet
    round_blade(blade_radius, blade_n_vertex, blade_angle_ratio,
                2 * domain_dept)

reservoir_plate(reservoir_length, domain_dept)
separator_1(separator_1_length, domain_dept, gap, gap_BP_distance,
            y_min_1 - 0.0005)
build_plate(bp_length, domain_dept)
separator_2(separator_2_length, domain_dept, gap, gap_BP_distance,
            y_min_1 - 0.0005)

print(f"{prm_file_name} has been written.")
print(f"Job is done!\n")
