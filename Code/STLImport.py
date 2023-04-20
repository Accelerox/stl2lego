import numpy as np
from stl import mesh
import trimesh
import random
import sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def ray_intersects_triangle(ray_origin, ray_direction, triangle):
    # Calculate the edges of the triangle
    edge1 = triangle[1] - triangle[0]
    edge2 = triangle[2] - triangle[0]

    # Calculate the determinant (h) and check if it's close to zero
    h = np.cross(ray_direction, edge2)
    a = np.dot(edge1, h)
    if a > -1e-8 and a < 1e-8:
        return False

    # Calculate the inverse of the determinant
    f = 1.0 / a

    # Calculate the first barycentric coordinate (u)
    s = ray_origin - triangle[0]
    u = f * np.dot(s, h)
    if u < 0.0 or u > 1.0:
        return False

    # Calculate the second barycentric coordinate (v)
    q = np.cross(s, edge1)
    v = f * np.dot(ray_direction, q)
    if v < 0.0 or u + v > 1.0:
        return False

    # Calculate the intersection point along the ray (t)
    t = f * np.dot(edge2, q)

    # If t is greater than a small positive value, the intersection point is valid
    if t > 1e-8:
        return True

    return False


def stl_to_voxel_array(stl_file, voxel_size):
    # Load the STL file
    loaded_mesh = trimesh.load_mesh(stl_file)

    # Check if the loaded_mesh is a Scene object, if so, extract the mesh
    if isinstance(loaded_mesh, trimesh.Scene):
        stl_mesh = loaded_mesh.dump(concatenate=True)
    else:
        stl_mesh = loaded_mesh

    # Calculate the bounding box of the STL mesh (returns x y z)
    min_coords = stl_mesh.bounds[0]
    max_coords = stl_mesh.bounds[1]

    print("min coords: " + str(min_coords) + ". max coords: " + str(max_coords))

    # Calculate the dimensions of the voxel grid
    grid_dimensions = np.ceil((max_coords - min_coords) / voxel_size).astype(int)

    print("Grid dimension: " + str(grid_dimensions))

    # Initialize the voxel grid
    voxel_grid = np.zeros(grid_dimensions, dtype=bool)

    # Loop through each voxel in the grid
    for x in range(grid_dimensions[0]):
        for y in range(grid_dimensions[1]):
            for z in range(grid_dimensions[2]):
                # Calculate the coordinates of the voxel's center
                voxel_center = min_coords + voxel_size * (np.array([x, y, z]) + 0.5)

                # Set the ray origin to the voxel center and use the direction pointing from the mesh's centroid to the voxel center
                ray_origin = voxel_center   
                ray_direction = (voxel_center - stl_mesh.centroid) / np.linalg.norm(voxel_center - stl_mesh.centroid)


                # Perform a ray-mesh intersection query
                locations, index_ray, index_tri = stl_mesh.ray.intersects_location(
                    ray_origins=[ray_origin], ray_directions=[ray_direction], multiple_hits=False
                )

                # If the number of intersections is odd, the voxel center is inside the mesh
                if len(locations) % 2 == 1:
                    voxel_grid[x, y, z] = 1

    return voxel_grid

def find_surface_voxels(voxel_array):
    """
    This functions finds the voxels which have a False neighbour (is connected to air) and returns a
    surface voxel numpy array

    Args:
        numpy voxel_array
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


def visualize_voxel_array(voxel_array):
    """
    This function takes a 3D numpy voxel array and plots it using matplotlib.
    
    Args:
        voxel_array
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a boolean mask of the voxel array
    voxel_mask = (voxel_array > 0)
    
    # Use the `voxels` method to create a voxel plot
    ax.voxels(voxel_mask, facecolors='blue', edgecolor='k')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


def main():

    # System arguments
    if len(sys.argv) != 4:
        print("Usage: python STILImport.py <filepath> <height> <hollow True/False>")
        sys.exit(1)

    # get command line arguments
    filepath = sys.argv[1]
    height = int(sys.argv[2])
    boolean = bool(int(sys.argv[3]))

    voxel_array = stl_to_voxel_array(filepath, height)
    #print(voxel_array)

    surface_voxels = find_surface_voxels(voxel_array)

    visualize_voxel_array(surface_voxels)

if __name__ == "__main__":
    main()
