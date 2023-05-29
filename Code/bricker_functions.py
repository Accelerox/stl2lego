"""
This script contains a collection of functions designed for generating, manipulating, and plotting 3D LEGO models.
The core functionality includes switching array axes, checking if a LEGO brick can be placed or is supported at a 
given position, placing bricks, and generating plots of completed models. In addition, bricks and their rotations 
are defined and colors are assigned for plotting.
"""

import itertools
import numpy as np
import json
import matplotlib.pyplot as plt
import time


def switch_axis_of_array(array, new_axes_order):
    """
    Transposes the given array to match the specified axis order.

    Parameters:
    array (numpy.ndarray): The array to transpose.
    new_axes_order (list): The new order for the axes. A list of three unique integers in the range [0, 2].

    Returns:
    numpy.ndarray: The transposed array.
    """
    if len(new_axes_order) != 3:
        raise ValueError("Invalid axes. Please provide a list of length 3.")
    if not all(0 <= axis <= 2 for axis in new_axes_order):
        raise ValueError("Invalid axes. Please provide axes between 0 and 2.")
    if len(set(new_axes_order)) != 3:
        raise ValueError("Invalid axes. Please provide unique axes.")

    return np.transpose(array, new_axes_order)


def can_place_brick(brick, volume_array, tiled_volume, z, y, x):
    """
    Determines whether a brick can be placed at a given position in the volume array.

    Parameters:
    brick (tuple): The dimensions of the brick.
    volume_array (numpy.ndarray): The 3D array representing the volume to be filled.
    tiled_volume (numpy.ndarray): The 3D array representing the filled volume.
    z, y, x (int): The coordinates in the volume array where the brick should be placed.

    Returns:
    bool: True if the brick can be placed at the given position, False otherwise.
    """
    for dz in range(brick[0]):
        for dy in range(brick[1]):
            for dx in range(brick[2]):
                if (
                    z + dz >= volume_array.shape[0]
                    or y + dy >= volume_array.shape[1]
                    or x + dx >= volume_array.shape[2]
                    or not volume_array[z + dz, y + dy, x + dx]
                    or tiled_volume[z + dz, y + dy, x + dx] == 1
                ):
                    return False
    return True



def is_brick_supported(brick, tiled_volume, z, y, x):
    """
    Checks if a brick at a given position is supported by another brick.

    Parameters:
    brick (tuple): The dimensions of the brick.
    tiled_volume (numpy.ndarray): The 3D array representing the filled volume.
    z, y, x (int): The coordinates in the volume array of the brick.

    Returns:
    bool: True if the brick is supported, False otherwise.
    """
    if z == 0:  # The brick is on the base layer, and it is supported by default
        return True

    for dz in range(brick[0]):
        for dy in range(brick[1]):
            for dx in range(brick[2]):
                # Check if there's a brick directly below
                if any(tiled_volume[z - 1, y + dy - bdy, x + dx - bdx] == 1
                       for bdy in range(brick[1])
                       for bdx in range(brick[2])):
                    return True

    return False


def place_brick(brick, tiled_volume, z, y, x, bricks_placed):
    """
    Places a brick in the volume and records its position.

    Parameters:
    brick (tuple): The dimensions of the brick.
    tiled_volume (numpy.ndarray): The 3D array representing the filled volume.
    z, y, x (int): The coordinates in the volume array where the brick should be placed.
    bricks_placed (list): A list of bricks that have been placed and their positions.
    """
    for dz in range(brick[0]):
        for dy in range(brick[1]):
            for dx in range(brick[2]):
                tiled_volume[z + dz, y + dy, x + dx] = 1
    bricks_placed.append({"brick": brick, "position": (z, y, x)})


def plot_legos(tiled_volume, volume_array):
    """
    Plots the LEGO model using matplotlib, given the final tiled volume and the volume array.

    Parameters:
    tiled_volume (numpy.ndarray): The 3D array representing the filled volume.
    volume_array (numpy.ndarray): The 3D array representing the volume to be filled.
    """
    # Create a new figure for the plot
    fig = plt.figure()
    # Add a 3D subplot to the figure
    ax = fig.add_subplot(111, projection="3d")

    # Get the dictionary of allowed bricks and their colors
    allowed_bricks_dict = generate_allowed_bricks()
    # Extract the keys (brick dimensions) from the dictionary
    allowed_lego_bricks = list(allowed_bricks_dict.keys())

    bricks_placed = []

    # Attempt to tile the volume with the allowed Lego bricks
    for z, y, x in itertools.product(range(volume_array.shape[0]), range(volume_array.shape[1]), range(volume_array.shape[2])):
        if volume_array[z, y, x] and not tiled_volume[z, y, x]:
            sorted_bricks = sorted(
                allowed_lego_bricks, key=lambda brick: brick[0] * brick[1] * brick[2], reverse=True)
            for brick in sorted_bricks:
                if can_place_brick(brick, volume_array, z, y, x) and is_brick_supported(brick, tiled_volume, z, y, x):
                    place_brick(brick, tiled_volume, z, y, x, bricks_placed)
                    ax.bar3d(x, y, z, brick[2], brick[1], brick[0], color=allowed_bricks_dict.get(
                        brick), shade=True)
                    # Stop iterating through bricks since one has been placed
                    break
    # Set the aspect ratio of x and y axes to be equal
    # You can change the values inside the list to adjust the aspect ratio
    ax.set_box_aspect([7.8, 7.8, 9.6])
    plt.gca().set_aspect('equal', adjustable='box')

    # Set the axis labels for the plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # Show the plot
    plt.show()


def center_plot_legos(tiled_volume, voxel_array):
    """
    Plots the LEGO model using matplotlib, given the final tiled volume and the volume array.
    This function attempts to tile the volume starting from the middle bottom.

    Parameters:
    tiled_volume (numpy.ndarray): The 3D array representing the filled volume.
    volume_array (numpy.ndarray): The 3D array representing the volume to be filled.
    """

    # Create a new figure for the plot
    fig = plt.figure()
    # Add a 3D subplot to the figure
    ax = fig.add_subplot(111, projection="3d")

    # Get the dictionary of allowed bricks and their colors
    allowed_bricks_dict = generate_allowed_bricks()
    # Extract the keys (brick dimensions) from the dictionary
    allowed_lego_bricks = list(allowed_bricks_dict.keys())

    bricks_placed = []

    # Calculate the middle indices for the volume array
    middle_indices = [dim // 2 for dim in voxel_array.shape]

    start_time = time.time()
    # Iterate through the volume array starting from the middle bottom
    for z, y, x in itertools.product(
        list(range(0, voxel_array.shape[0])),
        list(range(middle_indices[1], voxel_array.shape[1])
             ) + list(range(0, middle_indices[1])),
        list(range(middle_indices[2], voxel_array.shape[2])
             ) + list(range(0, middle_indices[2]))
    ):
        if voxel_array[z, y, x] and not tiled_volume[z, y, x]:
            sorted_bricks = sorted(
                allowed_lego_bricks, key=lambda brick: brick[0] * brick[1] * brick[2], reverse=True)

            for brick in sorted_bricks:
                if can_place_brick(brick, voxel_array, tiled_volume, z, y, x) and \
                        is_brick_supported(brick, tiled_volume, z, y, x):

                    place_brick(brick, tiled_volume, z, y, x, bricks_placed)

                    ax.bar3d(x, y, z, brick[2], brick[1], brick[0] * 9.6 /
                             7.8, color=allowed_bricks_dict.get(brick), shade=True)
                    # Stop iterating through bricks since one has been placed
                    break

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The optimizer took {elapsed_time} seconds to execute.")

    # Save the dictionary as a JSON file
    with open("latest_bricks_placed.json", "w") as json_file:
        json.dump(bricks_placed, json_file)

    # Set the aspect ratio of x and y axes to be equal
    # You can change the values inside the list to adjust the aspect ratio
    ax.set_box_aspect([7.8, 7.8, 9.6])
    plt.gca().set_aspect('equal', adjustable='box')

    # Set the axis labels for the plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # Show the plot
    plt.show()


def rotate_2D_coordinates(coordinates):
    """
    Returns the coordinates and their rotation in 2D.

    Parameters:
    coordinates (tuple): The x, y, and z coordinates.

    Returns:
    list: A list containing the original coordinates and their rotation.
    """
    x, y, z = coordinates
    return [(x, y, z), (x, z, y)]


def generate_allowed_bricks():
    """
    Generates a list of allowed LEGO brick sizes and their corresponding colors.

    Returns:
    dict: A dictionary of allowed LEGO bricks. The keys are strings representing 
    the brick dimensions and the values are their corresponding colors.
    """

    brick_list = {
        (1, 1, 1): "red",
        (1, 1, 2): "blue",
        (1, 2, 2): "green",
        (1, 2, 3): "orange",
        (1, 2, 4): "purple",
        (1, 4, 6): "grey",
        (1, 1, 3): "turquoise",
    }

    rotated_brick_list = {}

    for coords, color in brick_list.items():
        for rotated_coords in rotate_2D_coordinates(coords):
            rotated_brick_list[rotated_coords] = color

    print(rotated_brick_list)

    return rotated_brick_list
