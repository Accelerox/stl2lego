import itertools
import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from bricker_functions import *

# Load volume data from a JSON file
with open("Code/voxel_array.json", "r") as f:
    volume = json.load(f)

# Convert the nested list to a NumPy array and switches axises

new_axes_order = [2, 1, 0]  # [0, 1, 2] = [x,y, z] ergo same
volume_array = switch_axes(np.array(volume), new_axes_order)

# Initialize an array to store the tiled output
tiled_volume = np.zeros_like(volume_array, dtype=int)

#plot_legos(tiled_volume, volume_array)
center_plot_legos(tiled_volume, volume_array)
