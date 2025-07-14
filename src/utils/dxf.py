import ezdxf
import ezdxf.layouts
from ezdxf.math import ConstructionArc, Vec3, BSpline
import numpy as np
import math
import src.globals as globals



def CurvatureComb(element, density):
    ct = element.construction_tool()
    for t in np.linspace(0, ct.max_t, density):
        
        point, derivative = ct.derivative(t, 1)
        acceleration = ct.derivative(t, 2)

        curvature = np.linalg.norm(acceleration) / (np.linalg.norm(derivative) ** 3)
        adjusted_tangent_length = 0.1 / (1 + curvature)
        tangent = derivative.normalize(adjusted_tangent_length)
        if point[1] > 0:
            ppdclr = [-tangent[1], tangent[0], 0]
        else:
            ppdclr = [tangent[1], -tangent[0], 0]

        

        #msp.add_line(point, point + tangent, dxfattribs={"color": 1})
        #msp.add_line(point, point + ppdclr, dxfattribs={"color": 1})
        #try:
            #msp.add_line(old_point, point + ppdclr, dxfattribs={"color": 1})
        #except:
        #    NameError

        old_point = point + ppdclr

def calculate_length(points):
    length = 0
    for i in range(1, len(points)):
        length += Vec3(points[i]).distance(Vec3(points[i-1]))
    return length

def find_point_at_length(points, target_length):
    length = 0
    for i in range(1, len(points)):
        segment_length = Vec3(points[i]).distance(Vec3(points[i-1]))
        if length + segment_length >= target_length:
            ratio = (target_length - length) / segment_length
            return Vec3(points[i-1]) + (Vec3(points[i]) - Vec3(points[i-1])) * ratio
        length += segment_length
    return Vec3(points[-1])

'''
with open("E474.txt") as file:
    for line in file:
        try:
            x, y = map(float, line.split()) # split X and Y values into 
            AirfoilCoord.append([x,y])
        except ValueError: # skip lines that dont contain numeric data
            continue

for point in AirfoilCoord:
    z = 0
    point.append(z)

print(AirfoilCoord)

while AirfoilCoord[i][1] >= 0:
    PS_points.append(AirfoilCoord[i])
    i=i+1


i=len(PS_points)-1
print(i)
while i < len(AirfoilCoord):
    SS_points.append(AirfoilCoord[i])
    i=i+1

ps_matrix = np.array(PS_points)
ps_matrix = ps_matrix[::-1, :]
ss_matrix = np.array(SS_points)

print("PS points:")
print(ps_matrix)

print("SS points:")
print(ss_matrix)

doc = ezdxf.new()
msp = doc.modelspace()



# 1 unit = 1 [m]
unit = 'm'

if unit == 'm':
    scale = 1
if unit == 'mm':
    scale = 0.01

# 1 length = 1 unit 
length = 1.0



print("Scaled PS points:")
print(ps_matrix)

print("Scaled SS points:")
print(ss_matrix)

AirfoilCoord = np.array(AirfoilCoord)

#AirfoilCoord *= scale * length

#print(AirfoilCoord)

#Airfoil = msp.add_spline(AirfoilCoord)
#print(Airfoil.closed)

# Calculate 10% length of each spline
ps_length = calculate_length(ps_matrix)
ss_length = calculate_length(ss_matrix)

# Calculate the required length percentage for the arc
le_position = 0.02

# Find points at the new length percentage
ps_point_at_length = find_point_at_length(ps_matrix, ps_length * le_position)
ss_point_at_length = find_point_at_length(ss_matrix, ss_length * le_position)


# Create an arc with the specified radius
#print(ps_point_at_length)
#print(ss_point_at_length)
#print(arc_radius)

#arc = ConstructionArc.from_2p_radius(ps_point_at_length, ss_point_at_length, radius=arc_radius)

# Add the arc to the modelspace
#msp.add_arc(center=arc.center, radius=arc.radius, start_angle=arc.start_angle, end_angle=arc.end_angle)

#layout.page_setup(size=(24,18), margins=(1,1,1,1), units="inch")
'''
'''
paperspace.add_viewport(
    center=(14.5,2.5),
    size=(5,5),
    view_center_point=(12.5,7.5),
    view_height=5
)
'''
'''
ps_last_point = len(ps_matrix)-1
ss_last_point = len(ss_matrix)-1

print(ps_last_point)

print(ps_matrix[ps_last_point])
print(ss_matrix[ss_last_point])

if ps_matrix[ps_last_point][1] == ss_matrix[ss_last_point][1] and ps_matrix[ps_last_point][2] == ss_matrix[ss_last_point][2]:
    te_arc_center = ps_matrix[ps_last_point]

mod_te_ps = np.array([1.0, 0.0005, 0.0])
mod_te_ss = np.array([1.0, -0.0005, 0.0])

ps_matrix = ps_matrix[:-1]
ss_matrix = ss_matrix[:-1]

ps_matrix = np.vstack([ps_matrix, mod_te_ps])
ss_matrix = np.vstack([ss_matrix, mod_te_ss])

print(ps_matrix)
print(ss_matrix)

ps_matrix *= scale * length
ss_matrix *= scale * length

ps_last_point = len(ps_matrix)-1
ss_last_point = len(ss_matrix)-1

print(te_arc_center)

arc_radius = abs(mod_te_ps[1] - mod_te_ss[1])/2
print(arc_radius)

ps_spline = msp.add_spline(ps_matrix)
ss_spline = msp.add_spline(ss_matrix)

CurvatureComb(ps_spline, 100)
CurvatureComb(ss_spline, 100)

#le_spline = msp.add_spline([ps_matrix[2],ps_matrix[1],ps_matrix[0],ss_matrix[1],ss_matrix[2]])
#le_spline.dxf.end_tangent = (ps_matrix[2])
#le_spline.dxf.start_tangent = (ss_matrix[2])

ps_last_point = len(ps_matrix)-1
ss_last_point = len(ss_matrix)-1

#te_arc = ConstructionArc.from_2p_radius(start_point=(ss_matrix[ss_last_point][0],ss_matrix[ss_last_point][1]), end_point=(ps_matrix[ps_last_point][0],ps_matrix[ps_last_point][1]), radius=arc_radius)
#te_arc.add_to_layout(msp)

print('Saving file...')
doc.saveas("Airfoil.dxf")
'''

'''
i=len(PS_points)-1
print(i)
while i < len(AirfoilCoord):
    SS_points.append(AirfoilCoord[i])
    i=i+1

ps_matrix = np.array(PS_points)
ps_matrix = ps_matrix[::-1, :]
ss_matrix = np.array(SS_points)

print("PS points:")
print(ps_matrix)

print("SS points:")
print(ss_matrix)

doc = ezdxf.new()
msp = doc.modelspace()



# 1 unit = 1 [m]
unit = 'm'

if unit == 'm':
    scale = 1
if unit == 'mm':
    scale = 0.01

# 1 length = 1 unit 
length = 1.0



print("Scaled PS points:")
print(ps_matrix)

print("Scaled SS points:")
print(ss_matrix)

AirfoilCoord = np.array(AirfoilCoord)

#AirfoilCoord *= scale * length

#print(AirfoilCoord)

#Airfoil = msp.add_spline(AirfoilCoord)
#print(Airfoil.closed)

# Calculate 10% length of each spline
ps_length = calculate_length(ps_matrix)
ss_length = calculate_length(ss_matrix)

# Calculate the required length percentage for the arc
le_position = 0.02

# Find points at the new length percentage
ps_point_at_length = find_point_at_length(ps_matrix, ps_length * le_position)
ss_point_at_length = find_point_at_length(ss_matrix, ss_length * le_position)


# Create an arc with the specified radius
#print(ps_point_at_length)
#print(ss_point_at_length)
#print(arc_radius)

#arc = ConstructionArc.from_2p_radius(ps_point_at_length, ss_point_at_length, radius=arc_radius)

# Add the arc to the modelspace
#msp.add_arc(center=arc.center, radius=arc.radius, start_angle=arc.start_angle, end_angle=arc.end_angle)

#layout.page_setup(size=(24,18), margins=(1,1,1,1), units="inch")
'''
'''
paperspace.add_viewport(
    center=(14.5,2.5),
    size=(5,5),
    view_center_point=(12.5,7.5),
    view_height=5
)
'''

def export_airfoil_to_dxf(airfoil_idx, file_name=None):

    Z = 0
    
    doc = ezdxf.new()
    msp = doc.modelspace()

    airfoil = globals.PROJECT.project_airfoils[airfoil_idx]
    print(f"Exporting airfoil {airfoil_idx} to DXF...")
    
    #for idx, airfoil in enumerate(export_airfoil):

    if airfoil is not None and hasattr(airfoil, 'constr') and airfoil.constr['le'] is not None and len(airfoil.constr['le']) > 0:

        # Sprawdzenie, czy wszystkie tablice mają wystarczającą ilość danych
        if len(airfoil.constr['le'][0]) > 0 and len(airfoil.constr['le'][1]) > 0:
            exp_le = airfoil.constr['le']
        else:
            print(f"Airfoil {airfoil_idx} has an empty or insufficient LE array.")

        if len(airfoil.constr['ps'][0]) > 0 and len(airfoil.constr['ps'][1]) > 0:
            exp_ps = airfoil.constr['ps']
        else:
            print(f"Airfoil {airfoil_idx} has an empty or insufficient PS array.")

        if len(airfoil.constr['ss'][0]) > 0 and len(airfoil.constr['ss'][1]) > 0:
            exp_ss = airfoil.constr['ss']
        else:
            print(f"Airfoil {airfoil_idx} has an empty or insufficient SS array.")

        if len(airfoil.constr['te'][0]) > 0 and len(airfoil.constr['te'][1]) > 0:
            exp_te = airfoil.constr['te']
        else:
            print(f"Airfoil {airfoil_idx} has an empty or insufficient TE array.")


    ps_Z_row = np.full((1, exp_ps.shape[1]), Z)
    ps = np.vstack((exp_ps, ps_Z_row)).T
    #ps_spline = msp.add_spline(ps)
    ps_spline = msp.add_open_spline(ps)
    
    ss_Z_row = np.full((1, exp_ss.shape[1]), Z)
    ss = np.vstack((exp_ss, ss_Z_row)).T
    #ss_spline = msp.add_spline(ss)
    ss_spline = msp.add_open_spline(ss)

    le_Z_row = np.full((1, exp_le.shape[1]), Z)
    le = np.vstack((exp_le, le_Z_row)).T
    #le_spline = msp.add_spline(le)
    le_spline = msp.add_open_spline(le)

    te_Z_row = np.full((1, exp_te.shape[1]), Z)
    te = np.vstack((exp_te, te_Z_row)).T
    #te_spline = msp.add_spline(te)
    te_spline = msp.add_open_spline(te)

    doc.saveas("{}".format(file_name))
