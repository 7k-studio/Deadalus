'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

import numpy as np

def normalize(vector):
    length = sum(x ** 2 for x in vector) ** 0.5
    if length == 0:
        return vector
    return [x / length for x in vector]

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def lerp(start, end, t):
    return start + (end - start) * t

def deg2rad(degrees):
    import math
    return degrees * (math.pi / 180)

def rad2deg(radians):
    import math
    return radians * (180 / math.pi)

def convert_ndarray_to_list(obj):
    """Recursively convert numpy arrays in dict/list to lists."""
    if isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def convert_list_to_ndarray(obj):
    """Recursively convert lists in the object to numpy arrays where appropriate."""
    if isinstance(obj, list):
        # Only convert to ndarray if all elements are numbers or all are lists (for arrays of arrays)
        if all(isinstance(x, (int, float, complex)) for x in obj):
            return np.array(obj)
        elif all(isinstance(x, list) for x in obj):
            return np.array([convert_list_to_ndarray(x) for x in obj])
        else:
            return [convert_list_to_ndarray(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convert_list_to_ndarray(v) for k, v in obj.items()}
    else:
        return obj