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