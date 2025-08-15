#############################################################################
"""
Postprocessing graph tool.

By: Olivier Gaboriault
Date: December 19th, 2024
"""
#############################################################################
'''Importing Libraries'''
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# Configuration
# -------------------------------
binary_folder = "./00_binary/"
prm_file_names   = ["20_10_350", "20_20_250", "40_35_80"]  # your prm_file_name
label_list = ["PS1", "PS2", "PS3"]

list_of_layers = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#list_of_layers = np.array([0, 1, 2,3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])


n_cuts = np.load(binary_folder + 'number_of_cuts.npy')
for index, i in enumerate(prm_file_names):
    prefix = i
    # -------------------------------
    # Load Data
    # -------------------------------
    diameter_value = np.load(os.path.join(binary_folder, f'{prefix}_list_of_diameters.npy'))
    volume_fractions_all_layer = np.load(os.path.join(binary_folder, f'{prefix}_volume_fractions_all_layers.npy'))

    # -------------------------------
    # Process Data
    # -------------------------------
    # shape = (n_layers, 1, n_bins), squeeze to (n_layers, n_bins)
    
    for j in range(n_cuts):
        hist_matrix = volume_fractions_all_layer[:, j, :]
        n_layers, n_bins = hist_matrix.shape

        # Normalize each PSD for KDE-style shape comparison
        hist_matrix_normalized = hist_matrix / np.sum(hist_matrix, axis=1, keepdims=True)

        # -------------------------------
        # Plotting
        # -------------------------------
        plt.figure(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0, 1, list_of_layers.size))

        OG_PSD = np.array([0.14617, 0.16884, 0.16858, 0.15202, 0.12952, 0.10540, 0.07893, 0.05054])
        for layer in range(n_layers):
            if np.sum(layer == list_of_layers):
                plt.plot(diameter_value, hist_matrix_normalized[layer] - OG_PSD,
                     color=colors[layer],
                     linewidth=1.5,
                     label=f'Layer {layer+1}')


        

        plt.xlabel("Particle diameter [µm]")
        plt.ylabel(r"$\Delta$ volume fraction compared to original PSD")
        plt.title("Particle Size Distribution Evolution Over Layers - " + label_list[index] + f" - Section {j+1} / {n_cuts}")
        plt.grid(True)
        plt.legend(title="Layer", fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.ylim(-0.045, 0.045)
        plt.show()
