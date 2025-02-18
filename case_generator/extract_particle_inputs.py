#############################################################################
"""
Extraction particles properties and write them an particles.input file for
"file" insertion method.
"""
#############################################################################
'''Importing Libraries'''
import sys
import numpy as np
from lethe_pyvista_tools import *

#############################################################################

for it in range(15):
    prm_file_name = f"TI6AL4V-45-106_LOADING_{it:02}.prm"
    print(prm_file_name)
    pvd_name = 'out.pvd'
    output_file_name = f"particles_{it:02}.input"
    particle = lethe_pyvista_tools("./loading_prm/", prm_file_name, pvd_name)

    df = particle.get_df(-1)

    # Positions
    p_x = df.points[:, 0]
    p_y = df.points[:, 1]
    p_z = df.points[:, 2]

    # Velocity
    v_x = df["velocity"][:, 0]
    v_y = df["velocity"][:, 1]
    v_z = df["velocity"][:, 2]

    # Omega
    w_x = df["omega"][:, 0]
    w_y = df["omega"][:, 1]
    w_z = df["omega"][:, 2]

    # Diameter
    diameters = df["diameter"][:]


    counter = 0
    v_tot = 0

    with open(output_file_name, 'w') as file:
        # Write content to the file
        file.write(
            "p_x; p_y; p_z; v_x  ; v_y; v_z; w_x; w_y; w_z; diameters; fem_force_x; fem_force_y; fem_force_z; "
            "fem_torque_x; fem_torque_y; fem_torque_z \n")

        for px, py, pz, vx, vy, vz, wx, wy, wz, d in zip(p_x, p_y, p_z, v_x, v_y, v_z, w_x,
                                                                                       w_y, w_z, diameters):
            v_tot += 0.125 * 1.33333333333 * np.pi * d**3
            if px < 0.013:
                counter += 1
                file.write(
                    f"{px}; {py}; {pz}; {vx}; {vy}; {vz}; {wx}; {wy}; {wz}; {d};\n")

    print("Job is finish")
    print(counter)