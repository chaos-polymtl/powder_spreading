#############################################################################
"""
Postprocessing function for LPBF simulations

By: Olivier Gaboriault
Date: December 18th, 2024
"""

#############################################################################
# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lethe_pyvista_tools import *


def starting_times(n_layer, delta_n, plate_speed, first_starting_time, delta_starting_time, time_per_layer):
    """
    Input:
        n_layer : number of layer.
        delta_n : Layer thikness.
        plate_speed : Measuring plate average displacement speed.
        first_starting_time : Time at which the first blade start to move. 
        delta_starting_time : Time difference between two consecutive starting time. 
        time_per_layer : Time it takes for the blade to cross the domain in the x direction. 

    Output:
        Numpy array of float with the measuring time 
    """
    
    plate_displacement_time = delta_n / plate_speed
    every_starting_time = np.empty(n_layer)
    every_starting_time[0] = first_starting_time
    
    for j in range(1, n_layer):
        every_starting_time[j] = every_starting_time[j - 1] + time_per_layer * delta_starting_time
    
    return every_starting_time

def measuring_vtu_list(n_layer, time_step_list, measuring_time):
    """
    Input:
        n : number of layer.
        time_step_list : List of all the vtu time.
        measuring_time : Measuring time array.

    Output:
        Numpy array of the vtu index we want to analyze. 
    """
    vtu_measure = np.array([], dtype=int)
    
    # Index
    which_layer = 0

    for j, t in enumerate(time_step_list):
        if t >= measuring_time[which_layer]:
            vtu_measure = np.append(vtu_measure, int(j))
            which_layer += 1
            if which_layer == n_layer:
                break
            
    return vtu_measure