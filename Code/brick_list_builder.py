# Py script to generate the JSON file with allowed lego bricks

import json

def rotate_2D_coordinates(coordinates):
    x, y, z = coordinates
    return [(x, y, z), (x, z, y)]

brick_list = {
    (1, 1, 1): "red",
    (1, 1, 2): "blue",
    (1, 2, 2): "green",
}

rotated_brick_list = {}

for coords, color in brick_list.items():
    for rotated_coords in rotate_2D_coordinates(coords):
        rotated_brick_list[rotated_coords] = color

print(rotated_brick_list)

# Convert tuple keys to strings, as JSON only supports string keys
brick_list_str_keys = {str(key): value for key, value in brick_list.items()}

with open("allowed_brick_list.json", "w") as f:
    json.dump(brick_list_str_keys, f)
