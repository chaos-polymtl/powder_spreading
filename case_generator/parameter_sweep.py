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
labels = ["PS1", "PS2", "PS3"]
number_of_layers = 20
trans_friction   = [0.20, 0.20, 0.40]
rolling_friction = [0.10, 0.20, 0.36]
surface_energy   = [0.000350, 0.000250, 0.000080] 

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


for i, (t, r, s, label) in enumerate(zip(trans_friction, rolling_friction, surface_energy, labels)):

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
    case_gen(Case_prefix,directory_path, t,r,s, number_of_layers, 1)

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

    for v in range(2 + 1):

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
