import itertools
import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def get_allowed_bricks():
    with open("allowed_brick_list.json", "r") as f:
        allowed_brick_JSON = json.load(f)

    # Convert string keys back to tuples
    brick_dict = {tuple(map(int, key.strip("()").split(", "))): value for key, value in allowed_brick_JSON.items()}

    #allowed_lego_bricks = list(brick_colors.keys())

    return brick_dict

def switch_axes(array, new_axes_order):
    if len(new_axes_order) != 3:
        raise ValueError("Invalid axes. Please provide a list of length 3.")
    if not all(0 <= axis <= 2 for axis in new_axes_order):
        raise ValueError("Invalid axes. Please provide axes between 0 and 2.")
    if len(set(new_axes_order)) != 3:
        raise ValueError("Invalid axes. Please provide unique axes.")

    return np.transpose(array, new_axes_order)


def can_place_brick(brick, volume_array, z, y, x):
    for dz in range(brick[0]):
        for dy in range(brick[1]):
            for dx in range(brick[2]):
                if (
                    z + dz >= volume_array.shape[0]
                    or y + dy >= volume_array.shape[1]
                    or x + dx >= volume_array.shape[2]
                    or not volume_array[z + dz, y + dy, x + dx]
                ):
                    return False
    return True

def place_brick(brick, tiled_volume, z, y, x, bricks_placed):
    for dz in range(brick[0]):
        for dy in range(brick[1]):
            for dx in range(brick[2]):
                tiled_volume[z + dz, y + dy, x + dx] = 1
    bricks_placed.append({"brick": brick, "position": (z, y, x)})

def is_brick_supported(brick, tiled_volume, z, y, x):
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



def plot_legos(tiled_volume, volume_array):
    # Create a new figure for the plot
    fig = plt.figure()
    # Add a 3D subplot to the figure
    ax = fig.add_subplot(111, projection="3d")

    # Get the dictionary of allowed bricks and their colors
    allowed_bricks_dict = get_allowed_bricks()
    # Extract the keys (brick dimensions) from the dictionary
    allowed_lego_bricks = list(allowed_bricks_dict.keys())

    bricks_placed = []

        # Attempt to tile the volume with the allowed Lego bricks
    for z, y, x in itertools.product(range(volume_array.shape[0]), range(volume_array.shape[1]), range(volume_array.shape[2])):
        if volume_array[z, y, x] and not tiled_volume[z, y, x]:
            sorted_bricks = sorted(allowed_lego_bricks, key=lambda brick: brick[0] * brick[1] * brick[2], reverse=True)
            for brick in sorted_bricks:
                if can_place_brick(brick, volume_array, z, y, x) and is_brick_supported(brick, tiled_volume, z, y, x):
                    place_brick(brick, tiled_volume, z, y, x, bricks_placed)
                    ax.bar3d(x, y, z, brick[2], brick[1], brick[0], color=allowed_bricks_dict.get(brick), shade=True)
                    # Stop iterating through bricks since one has been placed
                    break
    # Set the aspect ratio of x and y axes to be equal
    ax.set_box_aspect([7.8, 7.8, 9.6]) # You can change the values inside the list to adjust the aspect ratio
    plt.gca().set_aspect('equal', adjustable='box')



    # Set the axis labels for the plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # Show the plot
    plt.show()

def center_plot_legos(tiled_volume, volume_array):
    # Create a new figure for the plot
    fig = plt.figure()
    # Add a 3D subplot to the figure
    ax = fig.add_subplot(111, projection="3d")

    # Get the dictionary of allowed bricks and their colors
    allowed_bricks_dict = get_allowed_bricks()
    # Extract the keys (brick dimensions) from the dictionary
    allowed_lego_bricks = list(allowed_bricks_dict.keys())

    bricks_placed = []

    # Calculate the middle indices for the volume array
    middle_indices = [dim // 2 for dim in volume_array.shape]

    # Iterate through the volume array starting from the middle bottom
    for z, y, x in itertools.product(
        list(range(0, volume_array.shape[0])),
        list(range(middle_indices[1], volume_array.shape[1])) + list(range(0, middle_indices[1])),
        list(range(middle_indices[2], volume_array.shape[2])) + list(range(0, middle_indices[2]))
    ):
        if volume_array[z, y, x] and not tiled_volume[z, y, x]:
            sorted_bricks = sorted(allowed_lego_bricks, key=lambda brick: brick[0] * brick[1] * brick[2], reverse=True)
            for brick in sorted_bricks:
                if can_place_brick(brick, volume_array, z, y, x) and is_brick_supported(brick, tiled_volume, z, y, x):
                    place_brick(brick, tiled_volume, z, y, x, bricks_placed)
                    ax.bar3d(x, y, z, brick[2], brick[1], brick[0] * 9.6/7.8, color=allowed_bricks_dict.get(brick), shade=True)
                    # Stop iterating through bricks since one has been placed
                    break
    # Save the dictionary as a JSON file
    with open("latest_bricks_placed.json", "w") as json_file:
        json.dump(bricks_placed, json_file)

    # Set the aspect ratio of x and y axes to be equal
    ax.set_box_aspect([7.8, 7.8, 9.6]) # You can change the values inside the list to adjust the aspect ratio
    plt.gca().set_aspect('equal', adjustable='box')

    # Set the axis labels for the plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # Show the plot
    plt.show()
