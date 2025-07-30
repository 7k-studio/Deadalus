# filepath: d:\Programy\AirFLOW\0.1.0\src\utils\step.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.globals as globals
import numpy as np
import datetime

def HEADER(file, base_name):
    file.write("ISO-10303-21;\n")
    file.write("HEADER;\n")
    file.write("FILE_DESCRIPTION(('AirFLOW Python STEP AP203 Export'), '1');\n")
    file.write(f"FILE_NAME('{base_name}','{datetime.datetime.now()}',(''),(''),'AirFLOW Python STEP AP203 Export','AirFLOW','');\n")
    file.write("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\n")
    
def ENDSEC_OPEN(file):
    file.write("ENDSEC;\n")
    file.write("\n")
    file.write("DATA;\n")

def FOOTER(file):
    file.write("ENDSEC;\n")
    file.write("END-ISO-10303-21;")

class CoordinatedUniversalTimeOffset:
    def __init__(self, idx):
        self.idx = idx
        self.a_or_b = '.AHEAD.'
    
    def export(self):
        return f"#{self.idx} = COORDINATED_UNIVERSAL_TIME_OFFSET ( 1, 0, {self.a_or_b} ) ;"
    
class DateTimeRole:
    def __init__(self, idx, role='NONE'):
        self.idx = idx
        self.role = role #creation date / classification_date
    
    def export(self):
        return f"#{self.idx} = DATE_TIME_ROLE ( '{self.role}' );"

class ApprovalStatus:
    def __init__ (self, idx, status='not_yet_approved'):
        self.idx = idx
        self.status = status
    
    def export(self):
        return f"#{self.idx} = APPROVAL_STATUS ( '{self.status}' ) ;"

class Approval:
    def __init__ (self, idx, status_idx=None, spec='UNSPECIFIED'):
        self.idx = idx
        self.status_idx = status_idx
        self.spec = spec
    
    def export(self):
        return f"#{self.idx} = APPROVAL ( #{self.status_idx}, '{self.spec}' ) ;"
    
class CCDesignAproval:
    def __init__(self, idx, approval_idx, pdfwss_idx):
        self.idx = idx
        self.approval_idx = approval_idx
        self.product_def_for_with_specified_source_idx = pdfwss_idx
    
    def export(self):
        return f"#{self.idx} = CC_DESIGN_APPROVAL ( #{self.approval_idx}, ( #{self.product_def_for_with_specified_source_idx} ) ) ;"

class ProductDefinitionFormationWithSpecifiedSource:
    def __init__(self, idx, product_idx):
        self.idx = idx
        self.var1 = 'ANY'
        self.var2 = ''
        self.product_idx = product_idx
        self.spec = '.NOT_KNOWN.'
    
    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE ( '{self.var1}', '{self.var2}', #{self.product_idx}, {self.spec} ) ;"

class SolidAngleUnit:
    def __init__(self, idx):
        self.idx = idx

    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) SI_UNIT ( $, .STERADIAN. ) SOLID_ANGLE_UNIT ( ) );"

class PlaneAngleUnit:
    def __init__(self, idx):
        self.idx = idx
    
    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, .RADIAN. ) );"

class LengthUnit:
    def __init__(self, idx):
        self.idx = idx
    
    def export(self):
        return f"#{self.idx} = ( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .MILLI., .METRE. ) );"

class UncertaintyMeasure:
    def __init__(self, idx, lu_idx):
        self.idx = idx
        self.length_unit_idx = lu_idx
    
    def export(self):
        return f"#{self.idx} = UNCERTAINTY_MEASURE_WITH_UNIT (LENGTH_MEASURE( 1.000000000000000082E-05 ), #{self.length_unit_idx}, 'distance_accuracy_value', 'NONE');"

class GeometricRepresentationContext:
    def __init__(self, idx, u_idx, lu_idx, sa_idx, pa_idx):
        self.idx = idx
        self.uncertatnity_idx = u_idx
        self.length_unit_idx = lu_idx
        self.solid_angle_idx = sa_idx
        self.plane_angle_idx = pa_idx
    
    def export(self):
        return f"#{self.idx} = ( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT ( ( #{self.uncertatnity_idx} ) ) GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #{self.length_unit_idx}, #{self.plane_angle_idx}, #{self.solid_angle_idx} ) ) REPRESENTATION_CONTEXT ( 'NONE', 'WORKSPACE' ) );"

class CartesianPoint:
    def __init__(self, idx, desc=None, X=None, Y=None, Z=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.X = X
        self.Y = Y
        self.Z = Z
    
    def export(self):
        return f"#{self.idx} = CARTESIAN_POINT ( '{self.desc}', ( {self.X}, {self.Y}, {self.Z} ) ) ;"
    
class VertexPoint:
    def __init__(self, idx, desc=None, cp_index=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.cartesian_point_idx = cp_index
    
    def export(self):
        return f"#{self.idx} = VERTEX_POINT ( '{self.desc}', #{self.cartesian_point_idx} ) ;"
 
class BsplineWithKnots:
    def __init__(self, idx, desc=None, points_indexes=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.num = 3
        self.points_indexes = points_indexes
        self.spec1 = '.UNSPECIFIED.'
        self.spec2 = '.F.'
        self.spec3 = '.F.'
        self.spec4 = [4,4]
        self.spec5 = [0.000000000000000000, 1.000000000000000000]
        self.spec6 = '.UNSPECIFIED.'
    
    def export(self):
        knots = ', '.join([f'#{i}' for i in self.points_indexes])
        return f"#{self.idx} = B_SPLINE_CURVE_WITH_KNOTS ( '{self.desc}', {self.num}, ( {knots} ), {self.spec1}, {self.spec2}, {self.spec3}, ( {self.spec4[0]}, {self.spec4[1]} ), ( {self.spec5[0]}, {self.spec5[1]} ), {self.spec6} ) ;"

class EdgeCurve:
    def __init__(self, idx, desc=None, VP1_idx=None, VP2_idx=None, Curv_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.vertex_point_1_idx = VP1_idx
        self.vertex_point_2_idx = VP2_idx
        self.curve_idx = Curv_idx
        self.spec = '.T.'
    
    def export(self):
        return f"#{self.idx} = EDGE_CURVE ( '{self.desc}', #{self.vertex_point_1_idx}, #{self.vertex_point_2_idx}, #{self.curve_idx}, {self.spec} ) ;"

class OrientedEdge:
    def __init__(self, idx, desc=None, ec_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.var2 = '*'
        self.var3 = '*'
        self.edge_curve_idx = ec_idx
        self.spec = '.F.'

    def export(self):
        return f"#{self.idx} = ORIENTED_EDGE ( '{self.desc}', {self.var2}, {self.var3}, #{self.edge_curve_idx}, {self.spec} ) ;"

class Plane:
    def __init__(self, idx, desc=None, ax_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.ax2_placement_idx = ax_idx
    
    def export(self):
        return f"#{self.idx} = PLANE ( '{self.desc}', #{self.ax2_placement_idx} ) ;"

class Axis2Placement3D:
    def __init__(self, idx, desc=None, cp_idx=None, dir1_idx=None, dir2_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.cp_idx = cp_idx
        self.dir1_idx = dir1_idx
        self.dir2_idx = dir2_idx
    
    def export(self):
        return f"#{self.idx} = AXIS2_PLACEMENT_3D ( '{self.desc}', #{self.cp_idx}, #{self.dir1_idx}, #{self.dir2_idx} ) ;"

class Direction:
    def __init__(self, idx, desc=None, vec=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.vec = vec
    
    def export(self):
        return f"#{self.idx} = DIRECTION ( '{self.desc}', ( {self.vec[0]}, {self.vec[1]}, {self.vec[2]} ) );"

class AdvancedFace:
    def __init__(self, idx, desc=None, fob_idx=None, p_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.face_outer_bound_idx = fob_idx
        self.plane_idx = p_idx
        self.spec = '.T.'

    def export(self):
        return f"#{self.idx} = ADVANCED_FACE ( '{self.desc}', ( #{self.face_outer_bound_idx} ), #{self.plane_idx}, {self.spec} ) ;"

class FaceOuterBounds:
    def __init__(self, idx, desc=None, el_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.edge_loop_idx = el_idx
        self.spec = '.T.'

    def export(self):
        return f"#{self.idx} = FACE_OUTER_BOUND ( '{self.desc}', #{self.edge_loop_idx}, {self.spec} ) ;"

class EdgeLoop:
    def __init__(self, idx, desc=None, OrientedEdge_list=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.OrientedEdge_list = OrientedEdge_list
    
    def export(self):
        oriented_edges = ', '.join([f'#{i}' for i in self.OrientedEdge_list])
        return f"#{self.idx} = EDGE_LOOP ( '{self.desc}', ( {oriented_edges} ) ) ;"

class ShellBasedSurfaceModel:
    def __init__(self, idx, desc=None, os_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.open_shell_idx = os_idx
    
    def export(self):
        return f"#{self.idx} = SHELL_BASED_SURFACE_MODEL ( '{self.desc}', ( #{self.open_shell_idx} ) ) ;"

class OpenShell:
    def __init__(self, idx, desc=None, af_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.advanced_face_list = af_idx
    
    def export(self):
        advanced_faces = ', '.join([f'#{i}' for i in self.advanced_face_list])
        return f"#{self.idx} = OPEN_SHELL ( '{self.desc}', ( {advanced_faces} ) ) ;"

class ManifoldSurfaceShapeRepresentation:
    def __init__(self, idx, desc=None, sbsm_idx=None, a2p3d_idx=None, gp_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.shell_based_surf_model_idx = sbsm_idx
        self.axis2_placement_3d_idx = a2p3d_idx
        self.geom_representation_idx = gp_idx
    
    def export(self):
        return f"#{self.idx} = MANIFOLD_SURFACE_SHAPE_REPRESENTATION ( '{self.desc}', ( #{self.shell_based_surf_model_idx}, #{self.axis2_placement_3d_idx} ), #{self.geom_representation_idx} ) ;"

class ShapeDefinitionRepresentation:
    def __init__(self, idx, mssr_idx):
        self.idx = idx
        self.product_def_shape_idx = 1000 #pds_idx bez tego zdaje się działać
        self.manifold_surf_shape_rep_idx = mssr_idx
    
    def export(self):
        return f"#{self.idx} = SHAPE_DEFINITION_REPRESENTATION ( #{self.product_def_shape_idx}, #{self.manifold_surf_shape_rep_idx} ) ;"

class Product:
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name
    def export(self):
        return f"#{self.idx} = PRODUCT ( '{self.name}', '{self.name}', '', ( #231 ) );"

class MechanicalContext:
    def __init__ (self, idx, desc=None, product_idx=None, context='mechanical'):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.app_context_idx = product_idx
        self.context = context
    
    def export(self):
        return f"#{self.idx} = MECHANICAL_CONTEXT ( '{self.desc}', #{self.app_context_idx} ) ;"

class ApplicationContext:
    def __init__(self, idx, context='parametrical 3d design of wings'):
        self.idx = idx
        self.context = context
    
    def export(self):
        return f"#{self.idx} = APPLICATION_CONTEXT ( '{self.context}' ) ;"
    
class ProductDefinitionShape:
    def __init__(self, idx, prod_idx):
        self.idx = idx
        self.prod_idx = prod_idx

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_SHAPE ( 'NONE', 'NONE', #{self.prod_idx} );"

class AdvancedBrepShapeRepresentation:
    def __init__(self, idx, name, brep_idx, axis_idx, context_idx):
        self.idx = idx
        self.filename = name
        self.brep_idx = brep_idx
        self.axis_idx = axis_idx
        self.context_idx = context_idx

    def export(self):
        return f"#{self.idx} = ADVANCED_BREP_SHAPE_REPRESENTATION ( '{self.filename}', ( #{self.brep_idx}, #{self.axis_idx} ), #{self.context_idx} );"

class ClosedShell:
    def __init__(self, idx, face_indices):
        self.idx = idx
        self.face_indices = face_indices

    def export(self):
        faces = ', '.join([f'#{i}' for i in self.face_indices])
        return f"#{self.idx} = CLOSED_SHELL ( 'NONE', ( {faces} ) );"

class BSplineSurfaceWithKnots:
    def __init__(self, idx, desc, u_degree, v_degree, spline_1, spline_2, spline_3, spline_4, knots_u, knots_v):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.u_degree = u_degree
        self.v_degree = v_degree
        self.spline_1 = spline_1
        self.spline_2 = spline_2
        self.spline_3 = spline_3
        self.spline_4 = spline_4
        self.knots_u = knots_u
        self.knots_v = knots_v

    def export(self):
        spline1 = ', '.join([f'#{i}' for i in self.spline_1])
        spline2 = ', '.join([f'#{i}' for i in self.spline_2])
        spline3 = ', '.join([f'#{i}' for i in self.spline_3])
        spline4 = ', '.join([f'#{i}' for i in self.spline_4])
        
        return (
            f"#{self.idx} = B_SPLINE_SURFACE_WITH_KNOTS ( '{self.desc}', {self.u_degree}, {self.v_degree}, ( \n"
            f"( {spline1} ),\n"
            f"( {spline2} ),\n"
            f"( {spline3} ),\n"
            f"( {spline4} )\n),\n.UNSPECIFIED., .F., .F., .F.,\n"
            f"( 4, 4 ),\n( 4, 4 ),\n"
            f"( {self.knots_u[0]}, {self.knots_u[1]} ),\n"
            f"( {self.knots_v[0]}, {self.knots_v[1]} ),\n.UNSPECIFIED. );"
        )

class GeometricSet:
    def __init__(self, idx, desc=None, group_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.group_idx = group_idx
    
    def export(self):
        return f"#{self.idx} = GEOMETRIC_SET ( '{self.desc}', ( {', '.join([f'#{idx}' for idx in self.group_idx])} ) ) ;"

class GeometricallyBoundedSurfaceShapeRepresentation:
    def __init__(self, idx, desc=None, gs_idx=0, gr_idx=0):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.geometric_set_idx = gs_idx
        self.geom_representation_idx = gr_idx 

    def export(self):
        return f"#{self.idx} = GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION ( '{self.desc}', ( #{self.geometric_set_idx} ), #{self.geom_representation_idx} ) ;"

def normalized_coords(x, y, z):
    return (
        float(round(x, 10)),
        float(round(y, 10)),
        float(round(z, 10))
    )

def _write_control_points(current_idx, segment, key):
    cp_store = []
    for i in range(len(segment.control_points[key][0, :])):
        coords = normalized_coords(
            segment.control_points[key][0, i],
            segment.control_points[key][1, i],
            segment.params['origin_Z'],
        )

        cp = CartesianPoint(current_idx, desc='Control Point', X=coords[0], Y=coords[1], Z=coords[2])
        cp_store.append(cp)
        current_idx += 1

    return current_idx, cp_store

def _write_vertex_edge(current_idx, segment, key):
    tmp = []
    cp_store = []
    ve_store = []
    for i in range(len(segment.control_points[key][0, :])):
        coords = normalized_coords(
            segment.control_points[key][0, i],
            segment.control_points[key][1, i],
            segment.params['origin_Z'],
        )
        cp = CartesianPoint(current_idx, desc='Control Point', X=coords[0], Y=coords[1], Z=coords[2])
        tmp.append(cp)
        current_idx += 1
        
    cp_store.append(tmp[0])
    cp_store.append(tmp[-1])

    for i in range(len(tmp)):  
        ve = VertexPoint(current_idx, f"End point {key}", tmp[i].idx)
        ve_store.append(ve)
        current_idx += 1

    return current_idx, cp_store, ve_store

def _write_b_spline(current_idx, construction_points, key):
    cp_indices = [obj.idx for obj in construction_points]
    bspline_ps = BsplineWithKnots(current_idx, key, cp_indices)
    current_idx += 1

    return current_idx, bspline_ps

def _write_edge_curve(current_idx, ve_points, bspline):
    ve_indices = [obj.idx for obj in ve_points]
    edge_curve = EdgeCurve(current_idx, None, ve_indices[0], ve_indices[1], bspline.idx)
    current_idx += 1

    return current_idx, edge_curve

def _write_oriented_edges(current_idx, edge_curve):
    oriented_edge = OrientedEdge(current_idx, None, edge_curve.idx)
    current_idx += 1
    
    return current_idx, oriented_edge

def _write_direction(current_idx, segment):
    P1 = [0,0,0]
    P2 = [1,0,0]
    P3 = [0,1,0]

    V1 = np.array(P2) - np.array(P1)
    V2 = np.array(P3) - np.array(P1)
    Vn = np.cross(V1,V2)

    V1_norm = V1 / np.linalg.norm(V1)
    Vn_norm = Vn / np.linalg.norm(Vn)

    direction_normal = Direction(current_idx, 'normal', Vn_norm) #normal Z
    current_idx += 1
    direction_tangential = Direction(current_idx, 'tangential', V1_norm) #X axis
    current_idx += 1

    return current_idx, direction_normal, direction_tangential

def _write_b_spline_surface(current_idx, wing_elements_store, i, side_key, front_key, rear_key):

    b_spline_surface = BSplineSurfaceWithKnots(current_idx, f'{side_key} b-spline surface', 3, 3, 
                                                  wing_elements_store[i-1][f'{side_key}_b_spline'], 
                                                  wing_elements_store[i-1][f'{front_key}_b_spline'], 
                                                  wing_elements_store[i-1][f'{rear_key}_b_spline'], 
                                                  wing_elements_store[i][f'{side_key}_b_spline'], 
                                                  0, 1)
    current_idx += 1

    surface_edge_loop = EdgeLoop(current_idx, f'{side_key} surface', [wing_elements_store[i-1][f'{side_key}_oriented_edge'].idx,
                                                    wing_elements_store[i-1][f'{front_key}_oriented_edge'].idx,
                                                    wing_elements_store[i-1][f'{rear_key}_oriented_edge'].idx,
                                                    wing_elements_store[i][f'{side_key}_oriented_edge'].idx])
    current_idx += 1
                                                     
    face_outer_bound = FaceOuterBounds(current_idx, f'{side_key} surface', surface_edge_loop.idx)
    current_idx += 1

    advanced_face = AdvancedFace(current_idx, f'{side_key} surface', face_outer_bound.idx, b_spline_surface.idx)
    current_idx += 1

    return current_idx, b_spline_surface, surface_edge_loop, face_outer_bound, advanced_face

def _write_unit_settings(current_idx, all_elements_store):

    solid_angle_unit = SolidAngleUnit(current_idx)
    current_idx += 1
    plane_angle_unit = PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = LengthUnit(current_idx)
    current_idx += 1
    uncertainty_measure = UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
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

    solid_angle_unit = SolidAngleUnit(current_idx)
    current_idx += 1
    plane_angle_unit = PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = LengthUnit(current_idx)
    current_idx += 1
    uncertainty_measure = UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
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
                geometric_set = GeometricSet(current_idx, None, cp_indices)
                all_elements_store.append(geometric_set)
                current_idx += 1

                geometrically_bounded_surface_shape_rep = GeometricallyBoundedSurfaceShapeRepresentation(current_idx, 'segment control points', geometric_set.idx, geometric_representation_context.idx)
                all_elements_store.append(geometrically_bounded_surface_shape_rep)
                current_idx += 1
            
    write_a_step_file(filepath, all_elements_store)

def export_2d_segment_wing(filepath, base_name):
    project = globals.PROJECT  # fallback for legacy use
    current_idx = 1

    all_elements_store = []

    solid_angle_unit = SolidAngleUnit(current_idx)
    current_idx += 1
    plane_angle_unit = PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = LengthUnit(current_idx)
    current_idx += 1
    uncertainty_measure = UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
    current_idx += 1

    all_elements_store.append(solid_angle_unit)
    all_elements_store.append(plane_angle_unit)
    all_elements_store.append(length_unit)
    all_elements_store.append(uncertainty_measure)
    all_elements_store.append(geometric_representation_context)

    for component in project.project_components:
        for wing in component.wings:
            for segment in wing.segments:

                print(f"ps: {segment.control_points['ps']}")
                print(f"ss: {segment.control_points['ss']}")
                print(f"le: {segment.control_points['le']}")
                print(f"te: {segment.control_points['te']}")

                # === PRESSURE SIDE ===
                current_idx, ps_control_points = _write_control_points(current_idx, segment, 'ps')
                current_idx, ps_ve_cp, ps_vertex_edges = _write_vertex_edge(current_idx, segment, 'ps')

                current_idx, ps_b_spline = _write_b_spline(current_idx, ps_control_points, 'ps')

                current_idx, ps_edge_curve = _write_edge_curve(current_idx, ps_vertex_edges, ps_b_spline)

                current_idx, ps_oriented_edge =_write_oriented_edges(current_idx, ps_edge_curve)

                for obj in ps_control_points:
                    all_elements_store.append(obj)
                for obj in ps_ve_cp:
                    all_elements_store.append(obj)
                for obj in ps_vertex_edges:
                    all_elements_store.append(obj)
                all_elements_store.append(ps_b_spline)
                all_elements_store.append(ps_edge_curve)
                all_elements_store.append(ps_oriented_edge)

                print(f'ps >>> is at idx: {current_idx}, CP: {len(ps_control_points)}, VE: {len(ps_vertex_edges)}, B-spline: {1 if ps_b_spline != None else 0}, EC: {1 if ps_edge_curve != None else 0}, OE: {1 if ps_oriented_edge != None else 0}')

                # === SUCTION SIDE ===
                current_idx, ss_control_points = _write_control_points(current_idx, segment, 'ss')
                current_idx, ss_ve_cp, ss_vertex_edges = _write_vertex_edge(current_idx, segment, 'ss')

                current_idx, ss_b_spline = _write_b_spline(current_idx, ss_control_points, 'ss')

                current_idx, ss_edge_curve = _write_edge_curve(current_idx, ss_vertex_edges, ss_b_spline)

                current_idx, ss_oriented_edge =_write_oriented_edges(current_idx, ss_edge_curve)

                for obj in ss_control_points:
                    all_elements_store.append(obj)
                for obj in ss_ve_cp:
                    all_elements_store.append(obj)
                for obj in ss_vertex_edges:
                    all_elements_store.append(obj)
                all_elements_store.append(ss_b_spline)
                all_elements_store.append(ss_edge_curve)
                all_elements_store.append(ss_oriented_edge)

                print(f'ss >>> is at idx: {current_idx}, CP: {len(ss_control_points)}, VE: {len(ss_vertex_edges)}, B-spline: {1 if ss_b_spline != None else 0}, EC: {1 if ss_edge_curve != None else 0}, OE: {1 if ss_oriented_edge != None else 0}')

                # === LEADING EDGE ===
                current_idx, le_control_points = _write_control_points(current_idx, segment, 'le')
                current_idx, le_ve_cp, le_vertex_edges = _write_vertex_edge(current_idx, segment, 'le')

                current_idx, le_b_spline = _write_b_spline(current_idx, le_control_points, 'le')

                current_idx, le_edge_curve = _write_edge_curve(current_idx, le_vertex_edges, le_b_spline)

                current_idx, le_oriented_edge =_write_oriented_edges(current_idx, le_edge_curve)

                for obj in le_control_points:
                    all_elements_store.append(obj)
                for obj in le_ve_cp:
                    all_elements_store.append(obj)
                for obj in le_vertex_edges:
                    all_elements_store.append(obj)
                all_elements_store.append(le_b_spline)
                all_elements_store.append(le_edge_curve)
                all_elements_store.append(le_oriented_edge)

                print(f'le >>> is at idx: {current_idx}, CP: {len(le_control_points)}, VE: {len(le_vertex_edges)}, B-spline: {1 if le_b_spline != None else 0}, EC: {1 if le_edge_curve != None else 0}, OE: {1 if le_oriented_edge != None else 0}')

                # === TRAILING EDGE ===
                current_idx, te_control_points = _write_control_points(current_idx, segment, 'te')
                current_idx, te_ve_cp, te_vertex_edges = _write_vertex_edge(current_idx, segment, 'te')

                current_idx, te_b_spline = _write_b_spline(current_idx, te_control_points, 'te')

                current_idx, te_edge_curve = _write_edge_curve(current_idx, te_vertex_edges, te_b_spline)

                current_idx, te_oriented_edge =_write_oriented_edges(current_idx, te_edge_curve)

                for obj in te_control_points:
                    all_elements_store.append(obj)
                for obj in te_ve_cp:
                    all_elements_store.append(obj)
                for obj in te_vertex_edges:
                    all_elements_store.append(obj)
                all_elements_store.append(te_b_spline)
                all_elements_store.append(te_edge_curve)
                all_elements_store.append(te_oriented_edge)

                print(f'te >>> is at idx: {current_idx}, CP: {len(te_control_points)}, VE: {len(te_vertex_edges)}, B-spline: {1 if te_b_spline != None else 0}, EC: {1 if te_edge_curve != None else 0}, OE: {1 if te_oriented_edge != None else 0}')

                # === Directions ===
                current_idx, seg_direction_nor, seg_direction_tan = _write_direction(current_idx, segment)

                all_elements_store.append(seg_direction_nor)
                all_elements_store.append(seg_direction_tan)

                axis2_placement_3d = Axis2Placement3D(current_idx, None, ps_control_points[0].idx, seg_direction_nor.idx, seg_direction_tan.idx)
                all_elements_store.append(axis2_placement_3d)
                current_idx += 1

                edge_loop = EdgeLoop(current_idx, None, [le_oriented_edge.idx, ps_oriented_edge.idx, te_oriented_edge.idx, ss_oriented_edge.idx] )
                all_elements_store.append(edge_loop)
                current_idx += 1

                face_outer_bound = FaceOuterBounds(current_idx, None, edge_loop.idx)
                all_elements_store.append(face_outer_bound)
                #fob_store.append(face_outer_bound)
                current_idx += 1

                plane = Plane(current_idx, None, axis2_placement_3d.idx)
                all_elements_store.append(plane)
                current_idx += 1

                advanced_face = AdvancedFace(current_idx, None, face_outer_bound.idx, plane.idx)
                all_elements_store.append(advanced_face)
                current_idx += 1

                open_shell = OpenShell(current_idx, None, advanced_face.idx)
                all_elements_store.append(open_shell)
                current_idx += 1

                shell_based_surface_model = ShellBasedSurfaceModel(current_idx, None, open_shell.idx)
                all_elements_store.append(shell_based_surface_model)
                current_idx += 1

                manifold_shape_surf_repersentation = ManifoldSurfaceShapeRepresentation(current_idx, f'{base_name}', shell_based_surface_model.idx, axis2_placement_3d.idx, geometric_representation_context.idx)
                all_elements_store.append(manifold_shape_surf_repersentation)
                current_idx += 1

                shape_definition_representation = ShapeDefinitionRepresentation(current_idx, manifold_shape_surf_repersentation.idx)
                all_elements_store.append(shape_definition_representation)
                current_idx += 1

                print(all_elements_store)
                
    write_a_step_file(filepath, base_name, all_elements_store)

def export_3d_segment_wing(filepath, base_name):
    project = globals.PROJECT  # fallback for legacy use
    current_idx = 1

    all_elements_store = []

    component_elements_store = []
    wing_elements_store = []

    solid_angle_unit = SolidAngleUnit(current_idx)
    current_idx += 1
    plane_angle_unit = PlaneAngleUnit(current_idx)
    current_idx += 1
    length_unit = LengthUnit(current_idx)
    current_idx += 1
    uncertainty_measure = UncertaintyMeasure(current_idx, length_unit.idx)
    current_idx += 1
    geometric_representation_context = GeometricRepresentationContext(current_idx, uncertainty_measure.idx, length_unit.idx, solid_angle_unit.idx, plane_angle_unit.idx)
    current_idx += 1

    all_elements_store.extend([
        solid_angle_unit,
        plane_angle_unit,
        length_unit,
        uncertainty_measure,
        geometric_representation_context
    ])

    for component in project.project_components:
        print(f"WNGWB > STEP_export >> Exporting component: {component.infos['name']} with {len(component.wings)} wings.")
        for wing in component.wings:
            print(f"WNGWB > STEP_export >> Exporting wing: {wing.infos['name']} with {len(wing.segments)} segments.")
            if len(wing.segments) > 1:
                print('WNGWB > STEP_export >> Warning: Wing has more than 1 segment, exporting to 3D.')
                for i in range(len(wing.segments)):

                    segment_elements_store = {}

                    segment = wing.segments[i]

                    #print(f"ps: {segment.control_points['ps']}")
                    #print(f"ss: {segment.control_points['ss']}")
                    #print(f"le: {segment.control_points['le']}")
                    #print(f"te: {segment.control_points['te']}")

                    # === PRESSURE SIDE ===
                    current_idx, ps_control_points = _write_control_points(current_idx, segment, 'ps')
                    current_idx, ps_ve_cp, ps_vertex_edges = _write_vertex_edge(current_idx, segment, 'ps')

                    current_idx, ps_b_spline = _write_b_spline(current_idx, ps_control_points, 'ps')
                    current_idx, ps_edge_curve = _write_edge_curve(current_idx, ps_vertex_edges, ps_b_spline)
                    current_idx, ps_oriented_edge =_write_oriented_edges(current_idx, ps_edge_curve)

                    # Store in dictionary
                    segment_elements_store['ps_control_points'] = ps_control_points
                    segment_elements_store['ps_ve_cp'] = ps_ve_cp
                    segment_elements_store['ps_vertex_edges'] = ps_vertex_edges
                    segment_elements_store['ps_b_spline'] = ps_b_spline
                    segment_elements_store['ps_edge_curve'] = ps_edge_curve
                    segment_elements_store['ps_oriented_edge'] = ps_oriented_edge

                    print(f'WNGWB > STEP_Export_3D > ps >>> is at idx: {current_idx}, CP: {len(ps_control_points)}, VE: {len(ps_vertex_edges)}, B-spline: {1 if ps_b_spline != None else 0}, EC: {1 if ps_edge_curve != None else 0}, OE: {1 if ps_oriented_edge != None else 0}')

                    # === SUCTION SIDE ===
                    current_idx, ss_control_points = _write_control_points(current_idx, segment, 'ss')
                    current_idx, ss_ve_cp, ss_vertex_edges = _write_vertex_edge(current_idx, segment, 'ss')

                    current_idx, ss_b_spline = _write_b_spline(current_idx, ss_control_points, 'ss')
                    current_idx, ss_edge_curve = _write_edge_curve(current_idx, ss_vertex_edges, ss_b_spline)
                    current_idx, ss_oriented_edge =_write_oriented_edges(current_idx, ss_edge_curve)

                    # Store in dictionary
                    segment_elements_store['ss_control_points'] = ss_control_points
                    segment_elements_store['ss_ve_cp'] = ss_ve_cp
                    segment_elements_store['ss_vertex_edges'] = ss_vertex_edges
                    segment_elements_store['ss_b_spline'] = ss_b_spline
                    segment_elements_store['ss_edge_curve'] = ss_edge_curve
                    segment_elements_store['ss_oriented_edge'] = ss_oriented_edge

                    print(f'WNGWB > STEP_export_3D >> ss >>> is at idx: {current_idx}, CP: {len(ss_control_points)}, VE: {len(ss_vertex_edges)}, B-spline: {1 if ss_b_spline != None else 0}, EC: {1 if ss_edge_curve != None else 0}, OE: {1 if ss_oriented_edge != None else 0}')

                    # === LEADING EDGE ===
                    current_idx, le_control_points = _write_control_points(current_idx, segment, 'le')
                    current_idx, le_ve_cp, le_vertex_edges = _write_vertex_edge(current_idx, segment, 'le')

                    current_idx, le_b_spline = _write_b_spline(current_idx, le_control_points, 'le')
                    current_idx, le_edge_curve = _write_edge_curve(current_idx, le_vertex_edges, le_b_spline)
                    current_idx, le_oriented_edge =_write_oriented_edges(current_idx, le_edge_curve)

                    # Store in dictionary
                    segment_elements_store['le_control_points'] = le_control_points
                    segment_elements_store['le_ve_cp'] = le_ve_cp
                    segment_elements_store['le_vertex_edges'] = le_vertex_edges
                    segment_elements_store['le_b_spline'] = le_b_spline
                    segment_elements_store['le_edge_curve'] = le_edge_curve
                    segment_elements_store['le_oriented_edge'] = le_oriented_edge

                    print(f'WNGWB > STEP_export_3D >> le >>> at idx: {current_idx}, CP: {len(le_control_points)}, VE: {len(le_vertex_edges)}, B-spline: {1 if le_b_spline != None else 0}, EC: {1 if le_edge_curve != None else 0}, OE: {1 if le_oriented_edge != None else 0}')

                    # === TRAILING EDGE ===
                    current_idx, te_control_points = _write_control_points(current_idx, segment, 'te')
                    current_idx, te_ve_cp, te_vertex_edges = _write_vertex_edge(current_idx, segment, 'te')

                    current_idx, te_b_spline = _write_b_spline(current_idx, te_control_points, 'te')
                    current_idx, te_edge_curve = _write_edge_curve(current_idx, te_vertex_edges, te_b_spline)
                    current_idx, te_oriented_edge =_write_oriented_edges(current_idx, te_edge_curve)

                    # Store in dictionary
                    segment_elements_store['te_control_points'] = te_control_points
                    segment_elements_store['te_ve_cp'] = te_ve_cp
                    segment_elements_store['te_vertex_edges'] = te_vertex_edges
                    segment_elements_store['te_b_spline'] = te_b_spline
                    segment_elements_store['te_edge_curve'] = te_edge_curve
                    segment_elements_store['te_oriented_edge'] = te_oriented_edge

                    print(f'WNGWB > STEP_export_3D >> te >>> at idx: {current_idx}, CP: {len(te_control_points)}, VE: {len(te_vertex_edges)}, B-spline: {1 if te_b_spline != None else 0}, EC: {1 if te_edge_curve != None else 0}, OE: {1 if te_oriented_edge != None else 0}')

                    # === LEADING EDGE <-> PRESSURE SIDE ===
                    if len(segment.control_points['le_ps']) != 0:
                        current_idx, le_ps_control_points = _write_control_points(current_idx, segment, 'le_ps')
                        current_idx, le_ps_ve_cp, le_ps_vertex_edges = _write_vertex_edge(current_idx, segment, 'le_ps')

                        current_idx, le_ps_b_spline = _write_b_spline(current_idx, le_ps_control_points, 'le_ps')
                        current_idx, le_ps_edge_curve = _write_edge_curve(current_idx, le_ps_vertex_edges, le_ps_b_spline)
                        current_idx, le_ps_oriented_edge =_write_oriented_edges(current_idx, le_ps_edge_curve)

                        # Store in dictionary
                        segment_elements_store['le_ps_control_points'] = le_ps_control_points
                        segment_elements_store['le_ps_ve_cp'] = le_ps_ve_cp
                        segment_elements_store['le_ps_vertex_edges'] = le_ps_vertex_edges
                        segment_elements_store['le_ps_b_spline'] = le_ps_b_spline
                        segment_elements_store['le_ps_edge_curve'] = le_ps_edge_curve
                        segment_elements_store['le_ps_oriented_edge'] = le_ps_oriented_edge

                        print(f'WNGWB > STEP_Export_3D >> le_ps >>> at idx: {current_idx}, CP: {len(le_ps_control_points)}, VE: {len(le_ps_vertex_edges)}, B-spline: {1 if le_ps_b_spline != None else 0}, EC: {1 if le_ps_edge_curve != None else 0}, OE: {1 if le_ps_oriented_edge != None else 0}')

                    # === TRAILING EDGE <-> PRESSURE SIDE ===
                    if len(segment.control_points['te_ps']) != 0:
                        current_idx, te_ps_control_points = _write_control_points(current_idx, segment, 'te_ps')
                        current_idx, te_ps_ve_cp, te_ps_vertex_edges = _write_vertex_edge(current_idx, segment, 'te_ps')

                        current_idx, te_ps_b_spline = _write_b_spline(current_idx, te_ps_control_points, 'te_ps')
                        current_idx, te_ps_edge_curve = _write_edge_curve(current_idx, te_ps_vertex_edges, te_ps_b_spline)
                        current_idx, te_ps_oriented_edge =_write_oriented_edges(current_idx, te_ps_edge_curve)

                        segment_elements_store['te_ps_control_points'] = te_ps_control_points
                        segment_elements_store['te_ps_ve_cp'] = te_ps_ve_cp
                        segment_elements_store['te_ps_vertex_edges'] = te_ps_vertex_edges
                        segment_elements_store['te_ps_b_spline'] = te_ps_b_spline
                        segment_elements_store['te_ps_edge_curve'] = te_ps_edge_curve
                        segment_elements_store['te_ps_oriented_edge'] = te_ps_oriented_edge

                        print(f'WNGWB > STEP_Export_3D >> te_ps >>> at idx: {current_idx}, CP: {len(te_ps_control_points)}, VE: {len(te_ps_vertex_edges)}, B-spline: {1 if te_ps_b_spline != None else 0}, EC: {1 if te_ps_edge_curve != None else 0}, OE: {1 if te_ps_oriented_edge != None else 0}')

                    # === LEADING EDGE <-> SUCTION SIDE ===
                    if len(segment.control_points['le_ss']) != 0:
                        current_idx, le_ss_control_points = _write_control_points(current_idx, segment, 'le_ss')
                        current_idx, le_ss_ve_cp, le_ss_vertex_edges = _write_vertex_edge(current_idx, segment, 'le_ss')

                        current_idx, le_ss_b_spline = _write_b_spline(current_idx, le_ss_control_points, 'le_ss')
                        current_idx, le_ss_edge_curve = _write_edge_curve(current_idx, le_ss_vertex_edges, le_ss_b_spline)
                        current_idx, le_ss_oriented_edge =_write_oriented_edges(current_idx, le_ss_edge_curve)

                        # Store in dictionary
                        segment_elements_store['le_ss_control_points'] = le_ss_control_points
                        segment_elements_store['le_ss_ve_cp'] = le_ss_ve_cp
                        segment_elements_store['le_ss_vertex_edges'] = le_ss_vertex_edges
                        segment_elements_store['le_ss_b_spline'] = le_ss_b_spline
                        segment_elements_store['le_ss_edge_curve'] = le_ss_edge_curve
                        segment_elements_store['le_ss_oriented_edge'] = le_ss_oriented_edge

                        print(f'WNGWB > STEP_Export_3D >> le_ss >>> at idx: {current_idx}, CP: {len(le_ss_control_points)}, VE: {len(le_ss_vertex_edges)}, B-spline: {1 if le_ss_b_spline != None else 0}, EC: {1 if le_ss_edge_curve != None else 0}, OE: {1 if le_ss_oriented_edge != None else 0}')

                    # === TRAILING EDGE <-> SUCTION SIDE ===
                    if len(segment.control_points['te_ss']) != 0:
                        current_idx, te_ss_control_points = _write_control_points(current_idx, segment, 'te_ss')
                        current_idx, te_ss_ve_cp, te_ss_vertex_edges = _write_vertex_edge(current_idx, segment, 'te_ss')

                        current_idx, te_ss_b_spline = _write_b_spline(current_idx, te_ss_control_points, 'te_ss')
                        current_idx, te_ss_edge_curve = _write_edge_curve(current_idx, te_ss_vertex_edges, te_ss_b_spline)
                        current_idx, te_ss_oriented_edge =_write_oriented_edges(current_idx, te_ss_edge_curve)

                        # Store in dictionary
                        segment_elements_store['te_ss_control_points'] = te_ss_control_points
                        segment_elements_store['te_ss_ve_cp'] = te_ss_ve_cp
                        segment_elements_store['te_ss_vertex_edges'] = te_ss_vertex_edges
                        segment_elements_store['te_ss_b_spline'] = te_ss_b_spline
                        segment_elements_store['te_ss_edge_curve'] = te_ss_edge_curve
                        segment_elements_store['te_ss_oriented_edge'] = te_ss_oriented_edge

                        print(f'WNGWB > STEP_Export_3D >> te_ss >>> at idx: {current_idx}, CP: {len(te_ss_control_points)}, VE: {len(te_ss_vertex_edges)}, B-spline: {1 if te_ss_b_spline != None else 0}, EC: {1 if te_ss_edge_curve != None else 0}, OE: {1 if te_ss_oriented_edge != None else 0}')

                    # === Directions ===
                    current_idx, seg_direction_nor, seg_direction_tan = _write_direction(current_idx, segment)

                    segment_elements_store['direction'] = [seg_direction_nor, seg_direction_tan]

                    axis2_placement_3d = Axis2Placement3D(current_idx, None, ps_control_points[0].idx, seg_direction_nor.idx, seg_direction_tan.idx)
                    segment_elements_store['axis2_placement_3d'] = axis2_placement_3d
                    current_idx += 1

                    edge_loop = EdgeLoop(current_idx, None, [le_oriented_edge.idx, ps_oriented_edge.idx, te_oriented_edge.idx, ss_oriented_edge.idx] )
                    segment_elements_store['edge_loop'] = edge_loop
                    current_idx += 1

                    face_outer_bound = FaceOuterBounds(current_idx, None, edge_loop.idx)
                    segment_elements_store['face_outer_bound'] = face_outer_bound
                    current_idx += 1

                    plane = Plane(current_idx, None, axis2_placement_3d.idx)
                    segment_elements_store['plane'] = plane
                    current_idx += 1

                    advanced_face = AdvancedFace(current_idx, None, face_outer_bound.idx, plane.idx)
                    segment_elements_store['advanced_face'] = advanced_face
                    current_idx += 1

                    #open_shell = OpenShell(current_idx, None, advanced_face.idx)
                    #segment_elements_store['open_shell'] = open_shell
                    #current_idx += 1

                    wing_elements_store.append(segment_elements_store)

                    #print('Segment Elements Store:', segment_elements_store)
                    print('Wing Elements Store:', wing_elements_store)

                    if i > 0:
                        current_idx, ps_b_spline_surface, ps_surface_edge_loop, ps_face_outer_bound, ps_advanced_face = _write_b_spline_surface(current_idx, wing_elements_store, i, 'ps', 'le_ps', 'te_ps')
                        current_idx, ss_b_spline_surface, ss_surface_edge_loop, ss_face_outer_bound, ss_advanced_face = _write_b_spline_surface(current_idx, wing_elements_store, i, 'ss', 'le_ss', 'te_ss')
                        current_idx, le_b_spline_surface, le_surface_edge_loop, le_face_outer_bound, le_advanced_face = _write_b_spline_surface(current_idx, wing_elements_store, i, 'le', 'le_ps', 'le_ss')
                        current_idx, te_b_spline_surface, te_surface_edge_loop, te_face_outer_bound, te_advanced_face = _write_b_spline_surface(current_idx, wing_elements_store, i, 'te', 'te_ps', 'te_ss')

                        segment_elements_store['ps_b_spline_surface'] = ps_b_spline_surface
                        segment_elements_store['ps_surface_edge_loop'] = ps_surface_edge_loop
                        segment_elements_store['ps_face_outer_bound'] = ps_face_outer_bound
                        segment_elements_store['ps_advanced_face'] = ps_advanced_face

                        segment_elements_store['ss_b_spline_surface'] = ss_b_spline_surface
                        segment_elements_store['ss_surface_edge_loop'] = ss_surface_edge_loop
                        segment_elements_store['ss_face_outer_bound'] = ss_face_outer_bound
                        segment_elements_store['ss_advanced_face'] = ss_advanced_face

                        segment_elements_store['le_b_spline_surface'] = le_b_spline_surface
                        segment_elements_store['le_surface_edge_loop'] = le_surface_edge_loop
                        segment_elements_store['le_face_outer_bound'] = le_face_outer_bound
                        segment_elements_store['le_advanced_face'] = le_advanced_face

                        segment_elements_store['te_b_spline_surface'] = te_b_spline_surface
                        segment_elements_store['te_surface_edge_loop'] = te_surface_edge_loop
                        segment_elements_store['te_face_outer_bound'] = te_face_outer_bound 
                        segment_elements_store['te_advanced_face'] = te_advanced_face

                        open_shell = OpenShell(current_idx, 'Wing from segment', [ps_advanced_face.idx, ss_advanced_face.idx, le_advanced_face.idx, te_advanced_face.idx])
                        segment_elements_store['open_shell'] = open_shell
                        current_idx += 1
                    
                wing_elements_store.append(segment_elements_store)

        shell_based_surface_model = ShellBasedSurfaceModel(current_idx, None, open_shell.idx)
        component_elements_store.append(shell_based_surface_model)
        current_idx += 1

        manifold_shape_surf_repersentation = ManifoldSurfaceShapeRepresentation(current_idx, f'{base_name}', shell_based_surface_model.idx, axis2_placement_3d.idx, geometric_representation_context.idx)
        component_elements_store.append(manifold_shape_surf_repersentation)
        current_idx += 1

        shape_definition_representation = ShapeDefinitionRepresentation(current_idx, manifold_shape_surf_repersentation.idx)
        component_elements_store.append(shape_definition_representation)
        current_idx += 1
    
    all_elements_store.append(component_elements_store)
    
    write_a_step_file(filepath, base_name, all_elements_store)

def write_a_step_file(filepath, base_name, all_elements_store):
    with open(filepath, "w") as file:
        HEADER(file, base_name)
        ENDSEC_OPEN(file)

        step_lines = []
        for component in all_elements_store:
            for segment_dict in component:
                for key, value in segment_dict.items():
                    if isinstance(value, (list, tuple, np.ndarray)):
                        for item in value:
                            if hasattr(item, "export"):
                                step_lines.append(item.export())
                    else:
                        if hasattr(value, "export"):
                            step_lines.append(value.export())
                else:
                    if hasattr(value, "export"):
                        step_lines.append(value.export())
            else:
                if hasattr(value, "export"):
                    step_lines.append(value.export())
        else:
            if hasattr(value, "export"):
                step_lines.append(value.export())

        for lines in step_lines:
            print(lines)
            file.write(lines + '\n')

        FOOTER(file)

def export_to_step(filepath, base_name):
    project = globals.PROJECT  # fallback for legacy use
    current_idx = 1

    all_elements_store = []
    wing_elements_store = []

    current_idx, all_elements_store = _write_unit_settings(current_idx, all_elements_store)

    if project.project_components[0]:
        if project.project_components[0].wings:
            if project.project_components[0].wings[0].segments:
                pass

if __name__ == "__main__":
    with open("file.step", "w") as file:
        HEADER(file)
        ENDSEC_OPEN(file)
        FOOTER(file)