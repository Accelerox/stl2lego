"""
This module contains functions for manipulating STL files, performing 
operations on meshes, and visualizing voxel arrays. The primary purpose of these
functions is to aid in the voxelization of 3D models.
"""

import numpy as np
import trimesh
import matplotlib.pyplot as plt
import json

from scipy.spatial.transform import Rotation


def rescale_mesh(stl_mesh, voxel_size, target_scale, height_dimension=2):
    """Rescales an STL mesh file to a certain height. Millimeters is used.

    Args:
        stl_mesh: The input STL mesh.
        voxel_size: The size of the voxel in each dimension.
        target_scale: The scale.
        height_dimension: The dimension to be treated as the height 
        (0 for x, 1 for y, 2 for z).
    """

    # Translate the mesh so that its lowest height_dimension-coordinate is at 0
    stl_mesh.vertices[:,
                      height_dimension] -= stl_mesh.bounds[0][height_dimension]

    # Calculate the scale factor based on the target height and voxel size
    # current_height = stl_mesh.bounds[1][height_dimension] - stl_mesh.bounds[0][height_dimension]
    scale_factor = target_scale

    # Scale the mesh by the voxel size in each dimension
    scale_factor *= voxel_size

    # Apply the scale factor
    stl_mesh.apply_scale(scale_factor)

    return stl_mesh


def set_z_axis_mesh(mesh: trimesh.Trimesh, new_z_axis_index: int) -> trimesh.Trimesh:
    """
    Sets a new z axis for a trimesh object.
    """
    # Ensure the provided axis index is valid (0 for X, 1 for Y, or 2 for Z)
    if new_z_axis_index not in [0, 1, 2]:
        raise ValueError("Invalid axis index. Must be 0, 1, or 2.")

    # Define the axes
    axes = np.identity(3)

    # Get the new Z-axis
    new_z_axis = axes[new_z_axis_index]

    # Compute the rotation between the current Z-axis and the new Z-axis
    current_z_axis = np.array([0, 0, 1])
    rotation = Rotation.from_rotvec(np.cross(current_z_axis, new_z_axis))

    # Convert the 3x3 rotation matrix to a 4x4 transformation matrix
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation.as_matrix()

    # Apply the transformation to the mesh
    mesh.apply_transform(transformation_matrix)

    return mesh


def align_tallest_dimension_with_z(stl_mesh):
    """
    Rotates the given STL mesh such that its tallest dimension is aligned with the Z axis.

    Args:
        stl_mesh: The input STL mesh.

    Returns:
        The rotated STL mesh.
    """

    # Calculate the size of the mesh along each axis
    size = stl_mesh.bounds[1] - stl_mesh.bounds[0]

    # Find the index of the tallest dimension
    tallest_dim_index = np.argmax(size)

    # If the tallest dimension is already the Z axis, no need to rotate
    if tallest_dim_index == 2:
        return stl_mesh

    # Otherwise, rotate the mesh to align the tallest dimension with the Z axis
    return set_z_axis_mesh(stl_mesh, tallest_dim_index)


def stl_to_voxel_array(stl_mesh, voxel_size, num_rays=3, seed=0) -> np.array:
    """
    Converts an STL mesh into a voxel representation. Voxels are set to True if their
    centers are within the geometry of the mesh.

    Args:
        stl_mesh: The input STL mesh.
        voxel_size: The size of the voxel in each dimension.
        num_rays: The number of rays to cast from each voxel.
        seed: The seed for the random number generator.

    Returns:
        A 3D numpy array representing the voxelized mesh.
    """

    # Set the seed for the random number generator
    np.random.seed(seed)

    # Calculate the bounding box of the STL mesh (returns x y z)
    min_coords = stl_mesh.bounds[0]
    max_coords = stl_mesh.bounds[1]

    print("min coords: " + str(min_coords) +
          ". max coords: " + str(max_coords))

    # Calculate the dimensions of the voxel grid
    grid_dimensions = np.ceil(
        (max_coords - min_coords) / voxel_size).astype(int)

    print("Grid dimension: " + str(grid_dimensions))

    # Initialize the voxel grid
    voxel_grid = np.zeros(grid_dimensions, dtype=bool)

    # Calculate the offset to align the voxel grid with the pyramid's centroid
    grid_offset = (grid_dimensions * voxel_size -
                   (max_coords - min_coords)) / 2

    # Loop through each voxel in the grid
    for x in range(grid_dimensions[0]):
        for y in range(grid_dimensions[1]):
            for z in range(grid_dimensions[2]):
                # Calculate the coordinates of the voxel's center
                voxel_center = min_coords + voxel_size * \
                    (np.array([x, y, z]) + 0.5) + grid_offset

                all_rays_inside = True  # Assume initially that all rays are inside

                for _ in range(num_rays):
                    # Generate a random unit vector
                    theta = np.random.uniform(0, 2*np.pi)
                    phi = np.random.uniform(0, np.pi)

                    ray_direction = np.array([np.sin(phi)*np.cos(theta), np.sin(phi)*np.sin(theta), np.cos(phi)])

                    # Perform a ray-mesh intersection query
                    locations, index_ray, index_tri = stl_mesh.ray.intersects_location(
                        ray_origins=[voxel_center], ray_directions=[
                            ray_direction], multiple_hits=False
                    )

                    # If the number of intersections is even, the voxel center is outside the mesh
                    if len(locations) % 2 == 0:
                        all_rays_inside = False
                        break  # No need to check the rest of the rays

                if all_rays_inside:
                    voxel_grid[x, y, z] = 1

    return voxel_grid



def find_surface_voxels(voxel_array) -> np.array:
    """
    Identifies the surface voxels in the voxel array. A voxel is considered a surface voxel 
    if it has a False neighbor.

    Args:
        voxel_array: 3D numpy array representing the voxel grid.

    Returns:
        A 3D numpy array of the same size as the input array, with True values 
        for surface voxels and False elsewhere.
    """
    surface_voxels = np.zeros_like(voxel_array, dtype=bool)

    for x in range(1, voxel_array.shape[0] - 1):
        for y in range(1, voxel_array.shape[1] - 1):
            for z in range(1, voxel_array.shape[2] - 1):
                if voxel_array[x, y, z]:
                    if (
                        not voxel_array[x - 1, y, z] or
                        not voxel_array[x + 1, y, z] or
                        not voxel_array[x, y - 1, z] or
                        not voxel_array[x, y + 1, z] or
                        not voxel_array[x, y, z - 1] or
                        not voxel_array[x, y, z + 1]
                    ):
                        surface_voxels[x, y, z] = True

    return surface_voxels


def plot_voxel_array(voxel_array, voxel_size):
    """
    Visualizes the given voxel array using matplotlib, where each voxel is 
    represented as a cube.

    Args:
        voxel_array: 3D numpy array representing the voxel grid.
        voxel_size: The size of each voxel in each dimension.
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the voxels using a single call to ax.voxels
    ax.voxels(voxel_array, edgecolor="k", facecolors="blue", linewidth=0.5)

    # Calculate the dimensions in millimeters
    voxel_size_mm = voxel_size
    max_dimensions = voxel_array.shape * voxel_size_mm

    # Find indices of True voxels
    true_voxels = np.argwhere(voxel_array)

    # Calculate the min and max indices in each dimension and add a buffer
    buffer = 5  # this can be adjusted
    min_x, min_y, min_z = true_voxels.min(axis=0) - buffer
    max_x, max_y, max_z = true_voxels.max(axis=0) + buffer

    # Set the axis limits to the min and max indices in each dimension 
    # (scaled by voxel size)
    ax.set_xlim(min_x * voxel_size_mm[0], max_x * voxel_size_mm[0])
    ax.set_ylim(min_y * voxel_size_mm[1], max_y * voxel_size_mm[1])
    ax.set_zlim(min_z * voxel_size_mm[2], max_z * voxel_size_mm[2])

    # Set the aspect ratio
    ax.set_box_aspect([voxel_size_mm[0], voxel_size_mm[1], voxel_size_mm[2]])

    # Set the axis labels with dimensions in millimeters
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')

    print("Voxel size:", voxel_size)
    print("True voxel indices (min):", true_voxels.min(axis=0))
    print("True voxel indices (max):", true_voxels.max(axis=0))
    print("Axis limits (x):", ax.get_xlim())
    print("Axis limits (y):", ax.get_ylim())
    print("Axis limits (z):", ax.get_zlim())

    plt.show()


def save_array_json(voxel_array: np.array, path: str):
    """
    Saves a numpy array as a json file at the specified path. The '.json' 
    extension is automatically added.

    Args:
        voxel_array: The numpy array to be saved.
        path: The directory path where the file is to be saved.
    """
    # convert to python nested list
    voxel_list = voxel_array.tolist()

    with open(path+'.json', 'w') as outfile:
        json.dump(voxel_list, outfile)


def stl_to_mesh(stl_path: str) -> trimesh.Trimesh:
    """
    Loads an STL file from a given path and returns a trimesh object.

    Args:
        stl_path: The path of the STL file.

    Returns:
        A trimesh object.
    """
    stl_mesh = trimesh.load_mesh(stl_path)

    # Check if the loaded_mesh is a Scene object, if so, extract the mesh
    if isinstance(stl_mesh, trimesh.Scene):
        stl_mesh = stl_mesh.dump(concatenate=True)
    else:
        stl_mesh = stl_mesh

    return stl_mesh
