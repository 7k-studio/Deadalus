'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DEADALUS.

DEADALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DEADALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DEADALUS.  If not, see <http://www.gnu.org/licenses/>.

'''
import logging
import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.globals as globals
import numpy as np
import datetime
import src.utils.tools_program as tools
import src.utils.step.class_step as STEP

logger = logging.getLogger(__name__)

class Deadalus2Step:
    def __init__(self):
        self.name = "Deadalus2Step203"
        self.description = "Deadalus Python STEP AP203 Export"
        self.version = "0.2.0-beta"
        self.schema = 'config_control_design'

def HEADER(file, base_name, script_obj):
    file.write("ISO-10303-21;\n")
    file.write("HEADER;\n")
    file.write(f"FILE_DESCRIPTION(('{script_obj.description}'), '1');\n")
    file.write(f"FILE_NAME('{base_name}','{datetime.datetime.now()}',(''),(''),'{script_obj.description}','{script_obj.name}','{script_obj.version}');\n")
    file.write(f"FILE_SCHEMA(('{script_obj.schema.upper()}'));\n")
    
def ENDSEC_OPEN(file):
    file.write("ENDSEC;\n")
    file.write("\n")
    file.write("DATA;\n")

def FOOTER(file):
    file.write("ENDSEC;\n")
    file.write("END-ISO-10303-21;")

def normalized_coords(x, y, z):
    return (
        float(round(x, 10)),
        float(round(y, 10)),
        float(round(z, 10))
    )


def _safe_unit_vector(p1, p2):
    v = np.array(p2, dtype=float) - np.array(p1, dtype=float)
    norm = np.linalg.norm(v)
    if norm <= 1e-12:
        # fallback direction never produce NaN
        return np.array([1.0, 0.0, 0.0])
    return v / norm


def _write_control_points(current_idx=None, uv_grid=None, key=None, ps_cp_grid=None, ss_cp_grid=None):
    
    cp_store = []
    
    rows = len(uv_grid)
    cols = len(uv_grid[0])

    logger.info(f"Recognized {rows}x{cols} UV grid")

    tmp_control_points_grid = [[0 for col in range(cols)] for row in range(rows)]

    for i in range(cols):
        for j in range(rows):
            coords = normalized_coords(
                uv_grid[j][i][0],
                uv_grid[j][i][1],
                uv_grid[j][i][2],
            )
            cp = STEP.CartesianPoint(current_idx, desc='Control Point', X=coords[0], Y=coords[1], Z=coords[2])
            tmp_control_points_grid[j][i] = cp
            cp_store.append(cp)
            current_idx += 1

    # if key == 'le':

    #     # LE <==> PS
    #     for k in range(cols):
    #         tmp_control_points_grid[0][k] = ps_cp_grid[0][k]

    #     # LE <==> SS
    #     for k in range(cols):
    #         tmp_control_points_grid[-1][k] = ss_cp_grid[0][k]
    
    # if key == 'te':
       
    #     # TE <==> SS
    #     for k in range(cols):
    #         tmp_control_points_grid[0][k] = ss_cp_grid[-1][k]

    #     # TE <==> PS
    #     for k in range(cols):
    #         tmp_control_points_grid[-1][k] = ps_cp_grid[-1][k]
    
    logger.info('\nControl Points')
    for i in range(rows):
        s = ""
        for j in range(cols):
            if tmp_control_points_grid[i][j] == 0:
                s += str(" - ")
            else:
                if (key == 'le' or key == 'te') and i == 0:
                    s += str(" ↕ ")
                elif (key == 'le' or key == 'te') and i == cols-1:
                    s += str(" ↕ ")
                else:
                    s += str(" X ")
        logger.info(s)

    return current_idx, cp_store, tmp_control_points_grid
    
def _write_vertex_point(current_idx: int=None, uv_grid_of_objects: list=None, key: str=None, ps_vp_grid: list=None, ss_vp_grid: list=None):
    vp_store = []

    rows = len(uv_grid_of_objects)
    cols = len(uv_grid_of_objects[0])

    logger.debug(rows, cols)

    max_u = cols - 1
    max_v = rows - 1

    tmp_vertex_points_grid = [[0 for col in range(cols)] for row in range(rows)]

    # if ps_vp_grid != None and ss_vp_grid != None:
    #     if key == 'le':
    #         tmp_vertex_points_grid[0][0]   = ps_vp_grid[0][0]
    #         tmp_vertex_points_grid[0][-1]  = ps_vp_grid[0][-1]
    #         tmp_vertex_points_grid[-1][0]  = ss_vp_grid[0][0]
    #         tmp_vertex_points_grid[-1][-1] = ss_vp_grid[0][-1]
    #     if key == 'te':
    #         tmp_vertex_points_grid[0][0]   = ps_vp_grid[-1][0]
    #         tmp_vertex_points_grid[0][-1]  = ps_vp_grid[-1][-1]
    #         tmp_vertex_points_grid[-1][0]  = ss_vp_grid[-1][0]
    #         tmp_vertex_points_grid[-1][-1] = ss_vp_grid[-1][-1]
    # else:    

    vp = STEP.VertexPoint(current_idx, f"End point {key}", uv_grid_of_objects[0][0].idx)
    tmp_vertex_points_grid[0][0] = vp
    vp_store.append(vp)
    current_idx += 1

    # Create Vertex Point of first point
    vp = STEP.VertexPoint(current_idx, f"End point {key}", uv_grid_of_objects[0][max_u].idx) #like a ps and le_ps point
    tmp_vertex_points_grid[0][max_u] = vp
    vp_store.append(vp)
    current_idx += 1

    # Create Vertex Point of last point 
    vp = STEP.VertexPoint(current_idx, f"End point {key}", uv_grid_of_objects[max_v][0].idx)
    tmp_vertex_points_grid[max_v][0] = vp
    vp_store.append(vp)
    current_idx += 1

    vp = STEP.VertexPoint(current_idx, f"End point {key}", uv_grid_of_objects[max_v][max_u].idx)
    tmp_vertex_points_grid[max_v][max_u] = vp
    vp_store.append(vp)
    current_idx += 1

    return current_idx, vp_store, tmp_vertex_points_grid

def _write_oriented_edge_from_uv_grid(current_idx, i, key, cp_uv_grid, vp_uv_grid, connection):
    spline_store = []
    ec_store = []
    oe_store = []
    dir_store = []
    vec_store = []

    if key in ['ps', 'ss']:
        txt = [f'{i} {key}', f'{i+1} {key}', f'{i} le_{key}', f'{i} te_{key}']
    if key in 'le':
        txt = [f'{i} le', f'{i+1} le', f'{i} le_ss', f'{i} le_ps']
    if key in 'te':
        txt = [f'{i} te', f'{i+1} te', f'{i} te_ps', f'{i} te_ss']

    rows = len(vp_uv_grid)
    cols = len(vp_uv_grid[0])

    max_u = cols - 1
    max_v = rows - 1

    if connection[0] == 'G0' and connection[1] == 'G0':

        # --- Create b spline from first column ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(rows):
            spline_construction_points.append(np.array(cp_uv_grid[j][0]).T.tolist())
            spline_vertex_points.append(np.array(vp_uv_grid[j][0]).T.tolist())
        bspline = STEP.BsplineWithKnots(current_idx, txt[0], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[0]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[0]}', edge_curve, 'F')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create line  from first row ---
        line_construction_points = []
        line_vertex_points = []
        for j in range(cols):
            line_construction_points.append(cp_uv_grid[0][j])
            line_vertex_points.append(vp_uv_grid[0][j])
        P1 = [line_construction_points[0].X, line_construction_points[0].Y, line_construction_points[0].Z]
        P2 = [line_construction_points[1].X, line_construction_points[1].Y, line_construction_points[1].Z]
        distance = np.linalg.norm(np.array(P1) - np.array(P2))

        if distance <= 1e-12:
            V1_norm = _safe_unit_vector(P1, P2)
        else:
            V1_norm = (np.array(P2) - np.array(P1)) / distance

        direction = STEP.Direction(current_idx, txt[2], V1_norm)
        dir_store.append(direction)
        current_idx += 1

        vector = STEP.Vector(current_idx, direction)
        vec_store.append(vector)
        current_idx += 1

        line = STEP.Line(current_idx, line_construction_points[0], vector, distance)
        current_idx += 1

        spline_store.append(line)
        ve_start = line_vertex_points[0]
        ve_end   = line_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'line {txt[2]}', ve_start, ve_end, line)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'line {txt[2]}', edge_curve, 'T')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create b spline from last column ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(rows):
            spline_construction_points.append(np.array(cp_uv_grid[j][-1]).T.tolist())
            spline_vertex_points.append(np.array(vp_uv_grid[j][-1]).T.tolist())
        bspline = STEP.BsplineWithKnots(current_idx, txt[1], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[1]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[1]}', edge_curve, 'T')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create b spline from last row ---
        line_construction_points = []
        line_vertex_points = []
        for j in range(cols):
            line_construction_points.append(cp_uv_grid[-1][j])
            line_vertex_points.append(vp_uv_grid[-1][j])

        P1 = [line_construction_points[0].X, line_construction_points[0].Y, line_construction_points[0].Z]
        P2 = [line_construction_points[1].X, line_construction_points[1].Y, line_construction_points[1].Z]
        distance = np.linalg.norm(np.array(P1) - np.array(P2))

        if distance <= 1e-12:
            # produce valid non-NaN vector for degenerate corner cases
            V1_norm = _safe_unit_vector(P1, P2)
        else:
            V1_norm = (np.array(P2) - np.array(P1)) / distance

        direction = STEP.Direction(current_idx, txt[3], V1_norm)
        dir_store.append(direction)
        current_idx += 1

        vector = STEP.Vector(current_idx, direction)
        vec_store.append(vector)
        current_idx += 1

        line = STEP.Line(current_idx, line_construction_points[0], vector, distance)
        current_idx += 1

        spline_store.append(line)
        ve_start = line_vertex_points[0]
        ve_end   = line_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'line {txt[3]}', ve_start, ve_end, line)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'line {txt[3]}', edge_curve, 'T')
        oe_store.append(oriented_edge)
        current_idx += 1
        

    else:
        # --- Create b spline from first column ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(rows):
            spline_construction_points.append(np.array(cp_uv_grid[j][0]).T.tolist())
            spline_vertex_points.append(np.array(vp_uv_grid[j][0]).T.tolist())
        bspline = STEP.BsplineWithKnots(current_idx, txt[0], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[0]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[0]}', edge_curve, 'F')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create b spline from first row ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(cols):
            spline_construction_points.append(cp_uv_grid[0][j])
            spline_vertex_points.append(vp_uv_grid[0][j])
        bspline = STEP.BsplineWithKnots(current_idx, txt[2], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[2]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[2]}', edge_curve, 'T')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create b spline from last column ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(rows):
            spline_construction_points.append(np.array(cp_uv_grid[j][-1]).T.tolist())
            spline_vertex_points.append(np.array(vp_uv_grid[j][-1]).T.tolist())
        bspline = STEP.BsplineWithKnots(current_idx, txt[1], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[1]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[1]}', edge_curve, 'T')
        oe_store.append(oriented_edge)
        current_idx += 1

        # --- Create b spline from last row ---
        spline_construction_points = []
        spline_vertex_points = []
        for j in range(cols):
            spline_construction_points.append(cp_uv_grid[-1][j])
            spline_vertex_points.append(vp_uv_grid[-1][j])
        bspline = STEP.BsplineWithKnots(current_idx, txt[3], spline_construction_points)
        current_idx += 1
        spline_store.append(bspline)
        ve_start = spline_vertex_points[0]
        ve_end   = spline_vertex_points[-1]
        edge_curve = STEP.EdgeCurve(current_idx, f'spline {txt[3]}', ve_start, ve_end, bspline)
        ec_store.append(edge_curve)
        current_idx += 1
        oriented_edge = STEP.OrientedEdge(current_idx, f'spline {txt[3]}', edge_curve, 'F')
        oe_store.append(oriented_edge)
        current_idx += 1

    return current_idx, oe_store, ec_store, spline_store, vec_store, dir_store

def _write_direction(current_idx, segment):
    P1 = [0,0,0]
    P2 = [1,0,0]
    P3 = [0,1,0]

    V1 = np.array(P2) - np.array(P1)
    V2 = np.array(P3) - np.array(P1)
    Vn = np.cross(V1,V2)

    V1_norm = V1 / np.linalg.norm(V1)
    Vn_norm = Vn / np.linalg.norm(Vn)

    direction_normal = STEP.Direction(current_idx, 'normal', Vn_norm) #normal Z
    current_idx += 1
    direction_tangential = STEP.Direction(current_idx, 'tangential', V1_norm) #X axis
    current_idx += 1

    return current_idx, direction_normal, direction_tangential

def _write_avanced_face_from_uv_grid(current_idx, key, cp_uv_grid, oriented_edge_store, spline_store):

    rows = len(cp_uv_grid)
    cols = len(cp_uv_grid[0])

    max_u = rows-1
    max_v = cols-1

    u_length = [0,max(spline_store[0].length, spline_store[2].length)]
    v_length = [0,max(spline_store[1].length, spline_store[3].length)]

    b_spline_surface = STEP.BSplineSurfaceWithKnots(current_idx, f'{key} b-spline surface', max_u, max_v, cp_uv_grid,u_length,v_length)
    current_idx += 1

    surface_edge_loop = STEP.EdgeLoop(current_idx, f'{key} surface', oriented_edge_store)
    current_idx += 1
                                                     
    face_outer_bound = STEP.FaceOuterBounds(current_idx, f'{key} surface', surface_edge_loop)
    current_idx += 1

    advanced_face = STEP.AdvancedFace(current_idx, f'{key} surface', face_outer_bound.idx, b_spline_surface)
    current_idx += 1

    return current_idx, b_spline_surface, surface_edge_loop, face_outer_bound, advanced_face

def _write_unit_settings(current_idx, all_elements_store):

    solid_angle_unit = STEP.SolidAngleUnit(current_idx, )
    current_idx += 1
    plane_angle_unit = STEP.PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = STEP.LengthUnit(current_idx, )
    current_idx += 1
    uncertainty_measure = STEP.UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = STEP.GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
    current_idx += 1

    all_elements_store.append(solid_angle_unit)
    all_elements_store.append(plane_angle_unit)
    all_elements_store.append(length_unit)
    all_elements_store.append(uncertainty_measure)
    all_elements_store.append(geometric_representation_context)

    return current_idx, all_elements_store

def export_only_control_points(filepath, base_name):
    project = globals.PROJECT  # fallback for legacy use
    current_idx = 1

    all_elements_store = []
    cp_store = []  # all unique CartesianPoints

    solid_angle_unit = STEP.SolidAngleUnit(current_idx)
    current_idx += 1
    plane_angle_unit = STEP.PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = STEP.LengthUnit(current_idx)
    current_idx += 1
    uncertainty_measure = STEP.UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = STEP.GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
    current_idx += 1

    all_elements_store.append(solid_angle_unit)
    all_elements_store.append(plane_angle_unit)
    all_elements_store.append(length_unit)
    all_elements_store.append(uncertainty_measure)
    all_elements_store.append(geometric_representation_context)

    for component in project.project_components:
        for wing in component.wings:
            for segment in wing.segments:

                # === PRESSURE SIDE ===
                current_idx, ps_control_points = _write_control_points(current_idx, segment, 'ps')

                # === SUCTION SIDE ===
                current_idx, ss_control_points = _write_control_points(current_idx, segment, 'ss')

                # === LEADING EDGE ===
                current_idx, le_control_points = _write_control_points(current_idx, segment, 'le')

                # === TRAILING EDGE ===
                current_idx, te_control_points = _write_control_points(current_idx, segment, 'te')

                cp_store.append(ps_control_points)
                cp_store.append(ss_control_points)
                cp_store.append(le_control_points)
                cp_store.append(te_control_points)

                cp_indices = [obj.idx for obj in cp_store]
                geometric_set = STEP.GeometricSet(current_idx, None, cp_indices)
                all_elements_store.append(geometric_set)
                current_idx += 1

                geometrically_bounded_surface_shape_rep = STEP.GeometricallyBoundedSurfaceShapeRepresentation(current_idx, 'segment control points', geometric_set.idx, geometric_representation_context.idx)
                all_elements_store.append(geometrically_bounded_surface_shape_rep)
                current_idx += 1
            
    write_a_step_file(filepath, all_elements_store)

def ensure_grid_connectivity(parent, child, key):

    grid = parent.uv_grid[key[0]]

    rows = len(grid)
    cols = len(grid[0])

    logger.debug(grid)

    # --- Modify first column ---
    for j in range(rows):
        logger.debug(parent.control_points[key[0]].T[j].tolist())
        grid[j][0] = parent.control_points[key[0]].T[j].tolist()

    # --- Modify first row ---
    for j in range(cols):
        logger.debug(parent.control_points[key[1]].T[j].tolist())
        grid[0][j] = parent.control_points[key[1]].T[j].tolist()

    # --- Modify last column ---
    for j in range(rows):
        logger.debug(child.control_points[key[2]].T[j].tolist())
        grid[j][-1] = child.control_points[key[2]].T[j].tolist()

    # --- Modify last row ---
    for j in range(cols):
        logger.debug(parent.control_points[key[3]].T[j].tolist())
        grid[-1][j] = parent.control_points[key[3]].T[j].tolist()

    logger.debug(grid)

    return grid

def export_3d_segment_wing(filepath, base_name):
    PROJECT = globals.PROJECT
    UNIT = globals.DEADALUS.preferences["general"]["units"]
    current_idx = 1

    all_elements_store = []
    component_elements_store = {}
    

    solid_angle_unit = STEP.SolidAngleUnit(current_idx, UNIT["angle"])
    current_idx += 1
    plane_angle_unit = STEP.PlaneAngleUnit(current_idx, UNIT["angle"])
    current_idx += 1
    length_unit = STEP.LengthUnit(current_idx, UNIT["length"])
    current_idx += 1
    uncertainty_measure = STEP.UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = STEP.GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
    current_idx += 1

    measurement_store = [
        solid_angle_unit,
        plane_angle_unit,
        length_unit,
        uncertainty_measure,
        geometric_representation_context
    ]

    for component in PROJECT.project_components:
        logger.info(f"Exporting component: {component.infos['name']} with {len(component.wings)} wings.")
        open_shell_list = []
        component_elements_store["wing"] = []
        for wing in component.wings:
            logger.info(f"Exporting wing: {wing.infos['name']} with {len(wing.segments)} segments.")
            wing_elements_store = {}
            tmp_wing_store = []
            tmp_surface_store = []
            if len(wing.segments) > 1:
                logger.info('NOTE: Wing has more than 1 segment, exporting to 3D.')
                for i in range(len(wing.segments)-1):

                    segment_elements_store = {}

                    segment = wing.segments[i]
                    connection = [wing.segments[i].anchor, wing.segments[i].anchor]

                    # === PRESSURE SIDE ===
                    uv_grid = ensure_grid_connectivity(wing.segments[i], wing.segments[i+1], ['ps','le_ps', 'ps', 'te_ps'])
                    current_idx, ps_c_point_store, ps_c_point_grid = _write_control_points(current_idx, uv_grid, 'ps')
                    current_idx, ps_v_point_store, ps_v_point_grid = _write_vertex_point(current_idx, ps_c_point_grid, 'ps')
                    current_idx, ps_o_edges_store, ps_e_curve_store, ps_b_splin_store, ps_vec_store, ps_dir_store = _write_oriented_edge_from_uv_grid(current_idx, i, 'ps', ps_c_point_grid, ps_v_point_grid, connection)
                    current_idx, ps_b_spline_surface, ps_surface_edge_loop, ps_face_outer_bound, ps_advanced_face = _write_avanced_face_from_uv_grid(current_idx, 'ps', ps_c_point_grid, ps_o_edges_store, ps_b_splin_store)

                    # Store in dictionary
                    segment_elements_store['ps_control_points'] = ps_c_point_store
                    segment_elements_store['ps_vertex_edges'] = ps_v_point_store
                    segment_elements_store['ps_directions'] = ps_dir_store
                    segment_elements_store['ps_vectors'] = ps_vec_store
                    segment_elements_store['ps_b_spline'] = ps_b_splin_store
                    segment_elements_store['ps_edge_curve'] = ps_e_curve_store
                    segment_elements_store['ps_oriented_edge'] = ps_o_edges_store
                    segment_elements_store['ps_b_spline_surface']  = ps_b_spline_surface
                    segment_elements_store['ps_surface_edge_loop'] = ps_surface_edge_loop
                    segment_elements_store['ps_face_outer_bound']  = ps_face_outer_bound
                    segment_elements_store['ps_advanced_face']     = ps_advanced_face

                    logger.info(f'PS >>> CP: {len(ps_c_point_store)}, VE: {len(ps_v_point_store)}, B-spline: {1 if ps_b_splin_store != None else 0}, EC: {1 if ps_e_curve_store != None else 0}, OE: {1 if ps_o_edges_store != None else 0}')

                    # === SUCTION SIDE ===
                    uv_grid = ensure_grid_connectivity(wing.segments[i], wing.segments[i+1], ['ss','le_ss', 'ss', 'te_ss'])
                    current_idx, ss_c_point_store, ss_c_point_grid = _write_control_points(current_idx, uv_grid, 'ss')
                    current_idx, ss_v_point_store, ss_v_point_grid = _write_vertex_point(current_idx, ss_c_point_grid, 'ss')
                    current_idx, ss_o_edges_store, ss_e_curve_store, ss_b_splin_store, ss_vec_store, ss_dir_store = _write_oriented_edge_from_uv_grid(current_idx, i, 'ss', ss_c_point_grid, ss_v_point_grid, connection)
                    current_idx, ss_b_spline_surface, ss_surface_edge_loop, ss_face_outer_bound, ss_advanced_face = _write_avanced_face_from_uv_grid(current_idx, 'ss', ss_c_point_grid, ss_o_edges_store, ss_b_splin_store)

                    # Store in dictionary
                    segment_elements_store['ss_control_points'] = ss_c_point_store
                    segment_elements_store['ss_vertex_edges'] = ss_v_point_store
                    segment_elements_store['ss_directions'] = ss_dir_store
                    segment_elements_store['ss_vectors'] = ss_vec_store
                    segment_elements_store['ss_b_spline'] = ss_b_splin_store
                    segment_elements_store['ss_edge_curve'] = ss_e_curve_store
                    segment_elements_store['ss_oriented_edge'] = ss_o_edges_store
                    segment_elements_store['ss_b_spline_surface']  = ss_b_spline_surface
                    segment_elements_store['ss_surface_edge_loop'] = ss_surface_edge_loop
                    segment_elements_store['ss_face_outer_bound']  = ss_face_outer_bound
                    segment_elements_store['ss_advanced_face']     = ss_advanced_face

                    logger.info(f'SS >>> CP: {len(ss_c_point_store)}, VE: {len(ss_v_point_store)}, B-spline: {1 if ss_b_splin_store != None else 0}, EC: {1 if ss_e_curve_store != None else 0}, OE: {1 if ss_o_edges_store != None else 0}')

                    # === LEADING EDGE ===
                    uv_grid = ensure_grid_connectivity(wing.segments[i], wing.segments[i+1], ['le','le_ss', 'le', 'le_ps'])
                    current_idx, le_c_point_store, le_c_point_grid = _write_control_points(current_idx, uv_grid, 'le')
                    current_idx, le_v_point_store, le_v_point_grid = _write_vertex_point(current_idx, le_c_point_grid, 'le')
                    current_idx, le_o_edges_store, le_e_curve_store, le_b_splin_store, le_vec_store, le_dir_store = _write_oriented_edge_from_uv_grid(current_idx, i, 'le', le_c_point_grid, le_v_point_grid, connection)
                    current_idx, le_b_spline_surface, le_surface_edge_loop, le_face_outer_bound, le_advanced_face = _write_avanced_face_from_uv_grid(current_idx, 'le', le_c_point_grid, le_o_edges_store, le_b_splin_store)

                    # Store in dictionary
                    segment_elements_store['le_control_points'] = le_c_point_store
                    segment_elements_store['le_vertex_edges'] = le_v_point_store
                    segment_elements_store['le_directions'] = le_dir_store
                    segment_elements_store['le_vectors'] = le_vec_store
                    segment_elements_store['le_b_spline'] = le_b_splin_store
                    segment_elements_store['le_edge_curve'] = le_e_curve_store
                    segment_elements_store['le_oriented_edge'] = le_o_edges_store
                    segment_elements_store['le_b_spline_surface']  = le_b_spline_surface
                    segment_elements_store['le_surface_edge_loop'] = le_surface_edge_loop
                    segment_elements_store['le_face_outer_bound']  = le_face_outer_bound
                    segment_elements_store['le_advanced_face']     = le_advanced_face

                    logger.info(f'LE >>> CP: {len(le_c_point_store)}, VE: {len(le_v_point_store)}, B-spline: {1 if le_b_splin_store != None else 0}, EC: {1 if le_e_curve_store != None else 0}, OE: {1 if le_o_edges_store != None else 0}')

                    # === TRAILING EDGE ===
                    uv_grid = ensure_grid_connectivity(wing.segments[i], wing.segments[i+1], ['te','te_ss', 'te', 'te_ps'])
                    current_idx, te_c_point_store, te_c_point_grid = _write_control_points(current_idx, uv_grid, 'te')
                    current_idx, te_v_point_store, te_v_point_grid = _write_vertex_point(current_idx, te_c_point_grid, 'te')
                    current_idx, te_o_edges_store, te_e_curve_store, te_b_splin_store, te_vec_store, te_dir_store = _write_oriented_edge_from_uv_grid(current_idx, i, 'te', te_c_point_grid, te_v_point_grid, connection)
                    current_idx, te_b_spline_surface, te_surface_edge_loop, te_face_outer_bound, te_advanced_face = _write_avanced_face_from_uv_grid(current_idx, 'te', te_c_point_grid, te_o_edges_store, te_b_splin_store)

                    # Store in dictionary
                    segment_elements_store['te_control_points'] = te_c_point_store
                    segment_elements_store['te_vertex_edges'] = te_v_point_store
                    segment_elements_store['te_directions'] = te_dir_store
                    segment_elements_store['te_vectors'] = te_vec_store
                    segment_elements_store['te_b_spline'] = te_b_splin_store
                    segment_elements_store['te_edge_curve'] = te_e_curve_store
                    segment_elements_store['te_oriented_edge'] = te_o_edges_store
                    segment_elements_store['te_b_spline_surface']  = te_b_spline_surface
                    segment_elements_store['te_surface_edge_loop'] = te_surface_edge_loop
                    segment_elements_store['te_face_outer_bound']  = te_face_outer_bound
                    segment_elements_store['te_advanced_face']     = te_advanced_face

                    logger.info(f'TE >>> CP: {len(te_c_point_store)}, VE: {len(te_v_point_store)}, B-splines: {len(te_b_splin_store)}, Edge Curves: {len(te_e_curve_store)}, Oriented Edges: {len(te_o_edges_store)}')

                    # === Directions ===
                    current_idx, seg_direction_nor, seg_direction_tan = _write_direction(current_idx, segment)

                    segment_elements_store['direction'] = [seg_direction_nor, seg_direction_tan]

                    axis2_placement_3d = STEP.Axis2Placement3D(current_idx, None, te_c_point_store[0].idx, seg_direction_nor.idx, seg_direction_tan.idx)
                    segment_elements_store['axis2_placement_3d'] = axis2_placement_3d
                    current_idx += 1

                    '''
                    # edge_loop = EdgeLoop(current_idx, None, [ps_o_edges_store[0], ps_o_edges_store[1], ps_o_edges_store[2], ps_o_edges_store[3]] )
                    # segment_elements_store['edge_loop'] = edge_loop
                    # current_idx += 1

                    # face_outer_bound = FaceOuterBounds(current_idx, None, edge_loop.idx)
                    # segment_elements_store['face_outer_bound'] = face_outer_bound
                    # current_idx += 1

                    # plane = Plane(current_idx, None, axis2_placement_3d.idx)
                    # segment_elements_store['plane'] = plane
                    # current_idx += 1

                    #advanced_face = AdvancedFace(current_idx, None, face_outer_bound.idx, plane.idx)
                    #segment_elements_store['advanced_face'] = advanced_face
                    #current_idx += 1

                    #open_shell = OpenShell(current_idx, None, advanced_face.idx)
                    #segment_elements_store['open_shell'] = open_shell
                    #current_idx += 1
                    '''
                    tmp_surface_store.append(ps_advanced_face)
                    tmp_surface_store.append(le_advanced_face)
                    tmp_surface_store.append(ss_advanced_face)
                    tmp_surface_store.append(te_advanced_face)
                    
                    
                    wing_elements_store[f"segment {i}"] = segment_elements_store
                    #logger.debug('Wing Elements Store:', wing_elements_store)

                open_shell = STEP.OpenShell(current_idx, 'Wing from segment', tmp_surface_store)
                wing_elements_store['open_shell'] = open_shell
                current_idx += 1

                open_shell_list.append(open_shell)

            component_elements_store["wing"].append(wing_elements_store)

        shell_based_surface_model = STEP.ShellBasedSurfaceModel(current_idx, None, open_shell_list)
        component_elements_store["shell_based_surface_model"] = shell_based_surface_model
        current_idx += 1

        manifold_shape_surf_repersentation = STEP.ManifoldSurfaceShapeRepresentation(current_idx, f'{base_name.replace(".step", "")}', shell_based_surface_model.idx, axis2_placement_3d.idx, geometric_representation_context.idx)
        component_elements_store["manifold_shape_surf_repersentation"] = manifold_shape_surf_repersentation
        current_idx += 1

        application_context = STEP.ApplicationContext(current_idx)
        component_elements_store["application_context"] = application_context
        current_idx += 1

        design_context = STEP.DesignContext(current_idx, application_context)
        component_elements_store["design_context"] = design_context
        current_idx += 1

        mechanical_context = STEP.MechanicalContext(current_idx, application_context_obj=application_context)
        component_elements_store["mechanical_context"] = mechanical_context
        current_idx += 1

        product = STEP.Product(current_idx, base_name.replace(".step", ""), mechanical_context)
        component_elements_store["product"] = product
        current_idx += 1

        product_definition_form_w_spec_source = STEP.ProductDefinitionFormationWithSpecifiedSource(current_idx, product)
        component_elements_store["product_definition_form_w_spec_source"] = product_definition_form_w_spec_source
        current_idx += 1

        product_definition = STEP.ProductDefinition(current_idx, prod_def_form_w_spec_source=product_definition_form_w_spec_source, design_context=design_context)
        component_elements_store["product_definition"] = product_definition
        current_idx += 1

        product_definition_shape = STEP.ProductDefinitionShape(current_idx, product_definition)
        component_elements_store["product_definition_shape"] = product_definition_shape
        current_idx += 1
        
        shape_definition_representation = STEP.ShapeDefinitionRepresentation(current_idx, product_definition_shape, manifold_shape_surf_repersentation)
        component_elements_store["shape_definition_representation"] = shape_definition_representation
        current_idx += 1
    
    all_elements_store.append(component_elements_store)
    
    write_a_step_file(filepath, base_name, measurement_store, all_elements_store)

def write_a_step_file(filepath, base_name, measurement_store, all_elements_store):
    D2Step = Deadalus2Step()
    def process_value(value, step_lines):
        """Append export() output of value or its elements to step_lines."""
        if isinstance(value, (list, tuple, np.ndarray)):
            for item in value:
                process_value(item, step_lines)
        elif isinstance(value, dict):
            for v in value.values():
                process_value(v, step_lines)
        else:
            if hasattr(value, "export"):
                step_lines.append(value.export())

    with open(filepath, "w") as file:
        HEADER(file, base_name, D2Step)
        ENDSEC_OPEN(file)

        step_lines = []

        # Process measurement store first
        for element in measurement_store:
            process_value(element, step_lines)

        # Process all other elements
        for component in all_elements_store:
            process_value(component, step_lines)

        # Write to file
        for line in step_lines:
            file.write(line + '\n')

        FOOTER(file)

def export_to_step(filepath, base_name):
    PROJECT = globals.PROJECT  # fallback for legacy use
    current_idx = 1

    all_elements_store = []
    wing_elements_store = []

    current_idx, all_elements_store = _write_unit_settings(current_idx, all_elements_store)

    if PROJECT.project_components[0]:
        if PROJECT.project_components[0].wings:
            if PROJECT.project_components[0].wings[0].segments:
                pass

if __name__ == "__main__":
    with open("file.step", "w") as file:
        HEADER(file)
        ENDSEC_OPEN(file)
        FOOTER(file)