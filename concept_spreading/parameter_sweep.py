"""
.sh case generator for calcul canada
By: Olivier Gaboriault
Date: February  21th, 2024
"""
import numpy as np
import jinja2
from datetime import datetime
import os
import shutil

# Loops
trans_friction = np.array([0.20])
rolling_friction = np.array([0.10])
surface_energy = np.array([0.000350])

# .sh  spreading
proc_per_node = 64           # Narval: 64 | Graham: 44 | Beluga: 40 | Cedar: 48
number_of_node = 1
time = 1 * 167               # In hours
memory = 249                 # Narval: 249 | Graham: 187 | Beluga: 92 | Cedar: 187
allocation = "rrg-blaisbru"  # "rrg-blaisbru" |  "def-blaisbru" | "def-damela"


BASE_PREFIX = "TI6AL4V-45-106"
Folder = "length_time_1_"

for i in range(len(trans_friction)):
    for j in range(len(rolling_friction)):
        for k in range(len(surface_energy)):
            CASE_PREFIX = f"{int(100 * trans_friction[i]):02d}_{int(100 * rolling_friction[j]):02d}_{int(1E6 * surface_energy[k]):02d}"

            # Define the directory path based on CASE_PREFIX
            directory_path = "./prm/" + CASE_PREFIX

            # Check if the directory already exists. If so, remove it.
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

            # Create the directory (which is now guaranteed not to exist)
            os.makedirs(directory_path)

            # Template processing and file writing
            PRM_FILE = BASE_PREFIX + ".prm"
            PATH = os.getcwd()
            templateLoader = jinja2.FileSystemLoader(searchpath=PATH)
            templateEnv = jinja2.Environment(loader=templateLoader)
            template = templateEnv.get_template(PRM_FILE)

            # Replace the values for the spreading prm
            output_text = template.render(Trans_friction=trans_friction[i],
                                          Rolling_friction=rolling_friction[j],
                                          Surface_energy=surface_energy[k])

            # New prm name
            prm_file_name = CASE_PREFIX + ".prm"
            output_file_path = os.path.join(directory_path, prm_file_name)

            # Write
            with open(output_file_path, 'w') as f:
                f.write(output_text)

            # Copy the gmsh folder
            dest_gmsh_dir = os.path.join(directory_path, "gmsh")
            shutil.copytree("./gmsh", dest_gmsh_dir)

            # Write the .sh
            SH_FILE = 'template.sh'
            templateLoader = jinja2.FileSystemLoader(searchpath=PATH)
            template = templateEnv.get_template(SH_FILE)

            # Replacing the symbols in the parameter file with the right expressions
            output_text = template.render(Account=allocation,
                                          Proc_per_node=str(proc_per_node),
                                          Number_of_node=str(number_of_node),
                                          Time=f"{time}:59:00",
                                          Memory=f"{memory}G",
                                          Job_name = CASE_PREFIX,
                                          Name=CASE_PREFIX)

            sh_file_name = CASE_PREFIX + ".sh"
            output_file_path = os.path.join(directory_path, sh_file_name)
            # Write the .sh
            with open(output_file_path, 'w') as f:
                f.write(output_text)

            #%%% Loading prms
            # Check how many layers there is to spread
            with open("./" + PRM_FILE, 'r') as file:
                lines = file.readlines()  # Read all lines into a list
            number_of_layers = int((lines[3]).split('=')[1])  # Check the right line

            print(f"{prm_file_name} has been written in {directory_path}")

print(f"Job is done!\n")
