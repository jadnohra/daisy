
def color_to_rgb(rgb_or_name):
    color_name_to_rgb = {"black": [0, 0, 0], 
                    "red": [1, 0, 0], "green": [0, 1, 0],
                    "blue": [0, 0, 1], "yellow": [1, 1, 0],
                    "orange": [1, 0.5, 0],
                    "white":[1,1,1]}
    if isinstance(rgb_or_name, str):
        return color_name_to_rgb[rgb_or_name]
    else:
        return rgb_or_name