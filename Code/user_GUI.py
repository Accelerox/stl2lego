import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from STL2JSON import *
import numpy as np


def STL_height(file_path):
    stl_mesh = mesh.Mesh.from_file(file_path)
    min_height, max_height = np.min(stl_mesh.z), np.max(stl_mesh.z)
    return max_height - min_height

def browse_file():
    file_path.set(filedialog.askopenfilename(filetypes=[("STL files", "*.stl")]))


def calculate_scale_and_call_function():
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
    user_call_STL2JSON_no_plot(file_path.get(), scale)



root_GUI = tk.Tk()
root_GUI.title("STL to LEGO")

file_path = tk.StringVar()
desired_height = tk.StringVar()
height_unit = tk.StringVar()

LEGO_BRICK_HEIGHT_MM = 9.6
original_stl_height = 1
if file_path.get() != '':
    try:
        STL_height(file_path.get()) # You should replace this with the height of the original STL
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
unit_dropdown = ttk.Combobox(frame2, textvariable=height_unit, values=unit_options, state="readonly", width=10)
unit_dropdown.pack(side=tk.LEFT)

convert_button = tk.Button(frame3, text="Convert", command=calculate_scale_and_call_function)
convert_button.pack(pady=10)

root_GUI.mainloop()
