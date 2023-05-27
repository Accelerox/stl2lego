#import itertools
#import numpy as np
#import json
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from bricker_functions import *
from STLImport import *
#from scipy.spatial.transform import Rotation
from stl import mesh
#import trimesh
#import random
import sys
import tkinter as tk
from tkinter import filedialog


def loading_screen(root, progress_var):
    root.title("Loading...")

    progress_label = tk.Label(root, textvariable=progress_var)
    progress_label.pack(pady=10)

    # Create a Canvas widget to display the animated GIF
    canvas = tk.Canvas(root, width=350, height=0)
    canvas.pack()

    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent closing the loading screen


def update_progress(root, progress_var, text):
    def update():
        progress_var.set(text)

    root.after(0, update)

def choose_file():
    return filedialog.askopenfilename()

def plot_function(tiled_volume, volume_array):
    #plot_legos(tiled_volume, volume_array)
    center_plot_legos(tiled_volume, volume_array)
    # Call center_plot_legos using the after method to ensure it runs in the main thread
    #root.after(0, center_plot_legos, tiled_volume, volume_array)
    #plt.show()

def user_call_STL2JSON_no_plot(stl_path, scale):
    # Initialize the loading screen
    root = tk.Tk()
    progress_var = tk.StringVar()
    progress_var.set("Starting...")
    loading_screen(root, progress_var)
    root.update()

    # Run the main code in a separate thread
    def run_code(root, stl_path, progress_var):
        # Update progress using the queue
        def update_progress_queue(text):
            progress_var.set(text)
            root.update()

        update_progress_queue("Loading STL file...")

        # Load and process the STL file
        #stl_path = choose_file(path_queue)

        update_progress_queue("Creating mesh object...")
        # Create a mesh object
        stl_mesh = stl_to_mesh(stl_path)

        # Rotate the STL mesh
        #stl_mesh = set_new_z_axis(stl_mesh, 2)

        # Align the tallest dimension of the mesh with the Z axis
        #stl_mesh = align_tallest_dimension_with_z(stl_mesh)

        update_progress_queue("Rescaling mesh...")
        # Rescale the STL mesh
        target_scale = scale
        voxel_size = np.array([7.8, 7.8, 9.6])
        stl_mesh = rescale_mesh(stl_mesh, voxel_size, target_scale)

        update_progress_queue("voxelizing...")
        # Convert the STL mesh to a voxel array
        volume_array = stl_to_voxel_array(stl_mesh, voxel_size)

        # Visualize the voxel array
        #plot_voxel_array(voxel_array, voxel_size)

        #save_array_json(voxel_array, "voxel_array")
    #--------------End Array maker---------

    # Convert the nested list to a NumPy array and switches axises
        new_axes_order = [2, 1, 0]  # [0, 1, 2] = [x,y, z] ergo same
        volume_array = switch_axes(np.array(volume_array), new_axes_order)

        # Initialize an array to store the tiled output
        tiled_volume = np.zeros_like(volume_array, dtype=int)
        update_progress_queue("placing blocks...")

        # Instead of calling the plotting functions directly, call the new plot_function
        root.after(0, plot_function, tiled_volume, volume_array)
        # Destroy the loading screen
        root.after(0, root.destroy)

    # Call 'run_code' with 'root', 'stl_path', and 'progress_var' as arguments
    run_code(root, stl_path, progress_var)

    # Start the main loop
    root.mainloop()

