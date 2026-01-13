"""
.sh case generator for calcul canada
By: Olivier Gaboriault
Date: February  21th, 2024
"""
import numpy as np
from datetime import datetime
from case_generator_function import *
import os
import shutil

# Loops
labels = ["A","B","C","D","E","F","G","H","I"]

number_of_layers = 20

trans_friction   = 0.20
rolling_friction = 0.10
surface_energy   = 0.000350

# PSD
og_mean = 5.946e-5
og_sigma = 1.232e-5
line_mean  = np.linspace(0.6 * og_mean,  og_mean, 3)
line_sigma = np.linspace(0.6 * og_sigma, og_sigma, 3)

# Create all combinations
means, sigmas = np.meshgrid(line_mean, line_sigma)

# Flatten the grid so we have 9 pairs
means  = means.flatten(order="F")
sigmas = sigmas.flatten(order="F")
# Transformation from volume to number weighted distribution
means  = means - 3. * sigmas * sigmas

# .sh  spreading
proc_per_node = 192          # Narval: 64 | Rorqual: 192 | Fir : 192
number_of_node = 1
time = 4 * 24 -1             # In hours
memory = 750                 # Narval: 249 | Rorqual: 750 | Fir: 750 |
allocation = "def-damela"  # "rrg-blaisbru" |  "def-blaisbru" | "def-damela"


# .sh  loading
proc_per_node_loading = 192          # Narval: 64 | Rorqual: 192 | Fir : 192
number_of_node_loading = 1
time_loading = 12                    # In hours
memory_loading =  750               # Narval: 249 | Rorqual: 750 | Fir: 750 |
allocation_loading = "def-damela"  # "rrg-blaisbru" |  "def-blaisbru" | "def-damela"


for i, (m, s, label) in enumerate(zip(means, sigmas, labels)):

    Case_prefix = label
    # Define the directory path based on Case_prefix
    directory_path = "./prm/" + Case_prefix
    loading_directory_path = directory_path + "/00_loading/"

    # Check if the directory already exists. If so, remove it.
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)

    if os.path.exists(loading_directory_path):
        shutil.rmtree(loading_directory_path)

    # Create the directory (which is now guaranteed not to exist)
    os.makedirs(directory_path)
    os.makedirs(loading_directory_path)

    # Create the .rpm
    case_gen(Case_prefix,directory_path, trans_friction,rolling_friction,surface_energy,m,s, number_of_layers)

    # Create the .sh
    SH_FILE = 'template.sh'
    PATH = os.getcwd()
    templateLoader = jinja2.FileSystemLoader(searchpath=PATH)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(SH_FILE)

    # Replacing the symbols in the parameter file with the right expressions
    output_text = template.render(Account=allocation,
                                  Proc_per_node=str(proc_per_node),
                                  Number_of_node=str(number_of_node),
                                  Time=f"{time}:59:00",
                                  Memory=f"{memory}G",
                                  Job_name = label,
                                  Name=Case_prefix + ".prm")

    sh_file_name = label + ".sh"
    output_file_path = os.path.join(directory_path, sh_file_name)
    #Write the .sh
    with open(output_file_path, 'w') as f:
        f.write(output_text)

    # Copy the gmsh folder in the loading directory
    dest_gmsh_dir = os.path.join(directory_path, "gmsh")
    if os.path.exists(dest_gmsh_dir):
        shutil.rmtree(dest_gmsh_dir)
    shutil.copytree("./gmsh", dest_gmsh_dir)

    for v in range(10 + 1):

        # Write the .sh
        SH_FILE = 'template.sh'
        templateLoader = jinja2.FileSystemLoader(searchpath=PATH)
        template = templateEnv.get_template(SH_FILE)
        loading_prm_file_name = label + "_LOADING_" + f"{v:02}" + ".prm"

        # Replacing the symbols in the parameter file with the right expressions
        output_text = template.render(Account=allocation_loading,
                                    Proc_per_node=str(proc_per_node_loading),
                                    Number_of_node=str(number_of_node_loading),
                                    Time=f"{time_loading}:00:00",
                                    Memory=f"{memory_loading}G",
                                    Job_name = f"{label}{v:02}",
                                    Name= loading_prm_file_name)

        sh_loading_file = label + "_LOADING_" + f"{v:02}" + ".sh"
        output_file_path = os.path.join(loading_directory_path, sh_loading_file)
        # Write the .sh
        with open(output_file_path, 'w') as f:
            f.write(output_text)

        # Copy the gmsh folder in the loading directory
        dest_gmsh_dir = os.path.join(loading_directory_path, "gmsh")
        print(dest_gmsh_dir)
        if os.path.exists(dest_gmsh_dir):
            shutil.rmtree(dest_gmsh_dir)
        shutil.copytree("./gmsh", dest_gmsh_dir)

print(f"Job is done!\n")
