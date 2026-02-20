#############################################################################
"""
Postprocessing graph tool.

By: Olivier Gaboriault
Date: December 19th, 2024
"""
#############################################################################

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#############################################################################
# Style configuration (publication-ready)
#############################################################################
figure_size_multiplier = 1.2
plt.rcParams.update({
    "lines.linewidth": 2 * figure_size_multiplier,
    "lines.markersize": 8 * figure_size_multiplier,
    "axes.linewidth": 1.2 * figure_size_multiplier,
    "xtick.major.width": 1.2 * figure_size_multiplier,
    "ytick.major.width": 1.2 * figure_size_multiplier,
})

color_palette = np.array(["#fa8738ff", "#4292c6ff", "#4fcd47ff",'#88419d','#810f7c','#4d004b',"black"])

markers = ['o', 's', 'D', '^', 'v', 'P', '*']

prm_file_names = ["PS1", "PS2", "PS3"]
L = "-L1"
labels = [name + L for name in prm_file_names]

plot_experimental_data = True

#############################################################################
# Robust paths (independent of launch location)
#############################################################################

BASE_DIR = Path(__file__).resolve().parent
exp_data_path = BASE_DIR / ".." / "experimental.data"
binary_folder = "00_binary/"
figures_dir = "00_figures/"

#############################################################################
# Figure setup
#############################################################################


plt.figure(figsize=(10 * figure_size_multiplier,
                    6 * figure_size_multiplier))

#############################################################################
# Experimental data
#############################################################################

if plot_experimental_data:

    layer_number, R1, R2, R3 = np.loadtxt(
        exp_data_path, skiprows=1, unpack=True
    )

    exp_avg = (R1 + R2 + R3) / 3

    # Cumulative relative density
    exp_cumulative = np.zeros_like(exp_avg)
    for i in range(1, len(exp_avg)):
        exp_cumulative[i] = np.sum(exp_avg[1:i+1]) / i

    exp_min = np.minimum.reduce([R1, R2, R3])
    exp_max = np.maximum.reduce([R1, R2, R3])
    exp_error = [exp_avg - exp_min, exp_max - exp_avg]

    # CRD (black dashed line)
    plt.plot(
        layer_number[1:] + 1,
        exp_cumulative[1:],
        linestyle='--',
        color='black',
        label="Experimental - CRD"
    )

    # LRD (black squares with black edge)
    plt.errorbar(
        layer_number + 1,
        exp_avg,
        yerr=exp_error,
        linestyle='-',
        marker='s',
        color='black',
        markerfacecolor='black',
        markeredgecolor='black',
        markeredgewidth=1.2,
        capsize=5,
        label="Experimental - LRD"
    )

#############################################################################
# Simulation data
#############################################################################

for index, prefix in enumerate(prm_file_names):

    CRD = np.load(binary_folder + prefix + '_CRD.npy')
    LRD = np.load(binary_folder + prefix + '_LRD.npy')

    print()
    print(f"Layer 1, {labels[index]} - LRD      : ", LRD[1])
    print(f"Maximum LRD value, {labels[index]} : ", np.max(LRD[2:]))
    print(f"Maximum LRD layer, {labels[index]} : ", np.argmax(LRD[2:]) + 2)
    print(f"Last layer CRD, {labels[index]} - CRD   : ", CRD[-1])

    color = color_palette[index]
    marker = markers[index]

    # LRD → solid + marker with black edge
    plt.plot(
        np.arange(1, len(LRD)),
        LRD[1:],
        linestyle='-',
        marker=marker,
        color=color,
        markerfacecolor=color,
        markeredgecolor='black',
        markeredgewidth=1.2,
        label=f"{labels[index]} - LRD"
    )

    # CRD → dashed line, same color, no marker
    plt.plot(
        np.arange(2, len(CRD)),
        CRD[2:],
        linestyle='--',
        color=color,
        label=f"{labels[index]} - CRD"
    )

#############################################################################
# Axes formatting
#############################################################################

plt.xlabel("Layer number", fontsize=24)
plt.ylabel("Relative density", fontsize=24)

plt.locator_params(axis='x', integer=True)
plt.xticks(np.arange(0, 21))
plt.tick_params(axis='both', which='major', labelsize=18)

#############################################################################
# Legend formatting (2 columns: LRD left, CRD right)
#############################################################################

handles, current_labels = plt.gca().get_legend_handles_labels()

sim_handles = [h for h, l in zip(handles, current_labels) if "Experimental" not in l]
sim_labels = [l for l in current_labels if "Experimental" not in l]

exp_handles = [h for h, l in zip(handles, current_labels) if "Experimental" in l]
exp_labels = [l for l in current_labels if "Experimental" in l]

left_col_h = [h for h, l in zip(sim_handles, sim_labels) if "LRD" in l] + \
             [h for h, l in zip(exp_handles, exp_labels) if "LRD" in l]

left_col_l = [l for l in sim_labels if "LRD" in l] + \
             [l for l in exp_labels if "LRD" in l]

right_col_h = [h for h, l in zip(sim_handles, sim_labels) if "CRD" in l] + \
              [h for h, l in zip(exp_handles, exp_labels) if "CRD" in l]

right_col_l = [l for l in sim_labels if "CRD" in l] + \
              [l for l in exp_labels if "CRD" in l]

plt.legend(
    left_col_h + right_col_h,
    left_col_l + right_col_l,
    loc='lower right',
    fontsize=14,
    ncol=2
)

#############################################################################
# Final layout and save
#############################################################################

plt.subplots_adjust(left=0.13, right=0.99, top=0.98, bottom=0.12)

plt.savefig(figures_dir + "/results.pdf", dpi=500)
# plt.show()

print("Job is done")
