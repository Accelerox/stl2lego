"""
-----------------------------------
STL to LEGO Converter - Main Script
-----------------------------------

Description:
-------------
This script provides an interface to transform STL (Stereolithography) 
3D model files into LEGO brick structures. The 3D models can be scaled according
to the desired height and unit of measure specified by the user.
This is accomplished by executing several operations such as mesh rotation, 
alignment, rescaling, conversion to voxel arrays and ultimately, plotting the structure.

Authors: Max Idermark & Mats Gard
"""

import tkinter as tk
import numpy as np

from tkinter import filedialog
from stl import mesh
from tkinter import ttk

from bricker_functions import *
from STLImport import *


def STL_height(file_path):
    stl_mesh = mesh.Mesh.from_file(file_path)
    min_height, max_height = np.min(stl_mesh.z), np.max(stl_mesh.z)
    return max_height - min_height


def loading_screen(root, progress_var):
    root.title("Loading...")

    progress_label = tk.Label(root, textvariable=progress_var)
    progress_label.pack(pady=10)

    # Create a Canvas widget to display the animated GIF
    canvas = tk.Canvas(root, width=350, height=0)
    canvas.pack()

    # Prevent closing the loading screen
    root.protocol("WM_DELETE_WINDOW", lambda: None)


def browse_file():
    file_path.set(filedialog.askopenfilename(
        filetypes=[("STL files", "*.stl")]))


def main_calculations(stl_path, scale):
    # Initialize the loading screen
    root = tk.Tk()
    progress_var = tk.StringVar()
    progress_var.set("Starting...")
    loading_screen(root, progress_var)
    root.update()

    # Create a mesh object
    stl_mesh = stl_to_mesh(stl_path)

    # Rotate the STL mesh
    # stl_mesh = set_new_z_axis(stl_mesh, 2)

    # Align the tallest dimension of the mesh with the Z axis
    # stl_mesh = align_tallest_dimension_with_z(stl_mesh)

    # Rescale the STL mesh
    target_scale = scale
    voxel_size = np.array([7.8, 7.8, 9.6])
    stl_mesh = rescale_mesh(stl_mesh, voxel_size, target_scale)

    # Convert the STL mesh to a voxel array
    voxel_array = stl_to_voxel_array(stl_mesh, voxel_size)

    # Visualize the voxel array
    # plot_voxel_array(voxel_array, voxel_size)

    save_array_json(voxel_array, "voxel_array")

    # Convert the nested list to a NumPy array and switches axises
    new_axes_order = [2, 1, 0]  # [0, 1, 2] = [x,y, z] ergo same
    voxel_array = switch_axis_of_array(np.array(voxel_array), new_axes_order)

    # Initialize an array to store the tiled output
    tiled_volume = np.zeros_like(voxel_array, dtype=int)

    # Instead of calling the plotting functions directly, call the new center_plot_legos
    root.after(0, center_plot_legos, tiled_volume, voxel_array)

    # Destroy the loading screen
    root.after(0, root.destroy)

    # Start the main loop
    root.mainloop()


def calculate_scale_and_call_function():
    """
    Function calls when 'Generete' button is pressed
    """

    height = float(desired_height.get())
    unit = height_unit.get()

    if unit == "cm":
        height = height * 10
    elif unit == "m":
        height = height * 1000

    if unit != "LEGO bricks":
        height = height / LEGO_BRICK_HEIGHT_MM
    original_stl_height = STL_height(file_path.get())
    print('OG hight', original_stl_height)
    scale = height / original_stl_height

    # Run the MAIN calculations
    main_calculations(file_path.get(), scale)


if __name__ == "__main__":

    root_GUI = tk.Tk()
    root_GUI.title("STL to LEGO")

    file_path = tk.StringVar()
    desired_height = tk.StringVar()
    height_unit = tk.StringVar()

    LEGO_BRICK_HEIGHT_MM = 9.6
    original_stl_height = 1
    if file_path.get() != '':
        try:
            # You should replace this with the height of the original STL
            STL_height(file_path.get())
        except Exception as e:
            print(f"Error: {e}")

    frame1 = tk.Frame(root_GUI)
    frame1.pack(padx=10, pady=10)
    frame2 = tk.Frame(root_GUI)
    frame2.pack(padx=10, pady=10)
    frame3 = tk.Frame(root_GUI)
    frame3.pack(padx=10, pady=10)

    label1 = tk.Label(frame1, text="Select STL file:")
    label1.pack(side=tk.LEFT)
    entry1 = tk.Entry(frame1, textvariable=file_path, width=30)
    entry1.pack(side=tk.LEFT)
    browse_button = tk.Button(frame1, text="Browse", command=browse_file)
    browse_button.pack(side=tk.LEFT)

    label2 = tk.Label(frame2, text="Desired height:")
    label2.pack(side=tk.LEFT)
    entry2 = tk.Entry(frame2, textvariable=desired_height, width=10)
    entry2.pack(side=tk.LEFT)

    unit_options = ["LEGO bricks", "cm", "m"]
    height_unit.set(unit_options[0])
    unit_dropdown = ttk.Combobox(
        frame2, textvariable=height_unit, values=unit_options, state="readonly", width=10)
    unit_dropdown.pack(side=tk.LEFT)

    # Start the program from the GUI and init all calls
    convert_button = tk.Button(
        frame3, text="Convert", command=calculate_scale_and_call_function)
    convert_button.pack(pady=10)

    root_GUI.mainloop()
