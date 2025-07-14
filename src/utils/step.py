# filepath: d:\Programy\AirFLOW\0.1.0\src\utils\step.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.globals as globals

def HEADER(file):
    file.write("ISO-10303-21;\n")
    file.write("HEADER;\n")
    file.write("FILE_DESCRIPTION(('AirFLOW Python STEP AP203 Export'), '1');\n")
    file.write("FILE_NAME('AirFLOW_Export.stp','2025-06-21T21:14:38',(''),(''),'AirFLOW Python STEP AP203 Export','AirFLOW','');\n")
    file.write("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));\n")
    
def ENDSEC_OPEN(file):
    file.write("ENDSEC;\n")
    file.write("DATA;\n")

def FOOTER(file):
    file.write("ENDSEC;\n")
    file.write("END-ISO-10303-21;")

def units(file, idx):
    file.write(f"#{idx} =( NAMED_UNIT ( * ) SI_UNIT ( $, .STERADIAN. ) SOLID_ANGLE_UNIT ( ) );\n")
    idx += 1
    file.write(f"#{idx} =( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, .RADIAN. ) );\n")
    idx += 1
    file.write(f"#{idx} =( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( .MILLI., .METRE. ) );\n")
    idx += 1
    file.write(f"#{idx} = UNCERTAINTY_MEASURE_WITH_UNIT (LENGTH_MEASURE( 1.000000000000000082E-05 ), #{idx-1}, 'distance_accuracy_value', 'NONE');\n")
    idx += 1
    file.write(f"#{idx} =( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT ( ( #{idx-1} ) ) GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #{idx-2}, #{idx-3}, #{idx-4} ) ) REPRESENTATION_CONTEXT ( 'NONE', 'WORKSPACE' ) );\n")
    geom_ctx_id = idx
    idx += 1

    return idx, geom_ctx_id
    


def export_simple_wing(filepath):
    """
    splines: dict z kluczami ['le', 'ps', 'ss', 'te'], każdy to (x_list, y_list)
    origin_Z: wysokość (opcjonalnie)
    """
    project = globals.PROJECT  # fallback for legacy use

    with open(filepath, "w") as file:
        HEADER(file)
        ENDSEC_OPEN(file)
        idx = 1
        point_ids = {}  # np. point_ids['le'] = [id1, id2, ...]

        for component in project.project_components:
            for wing in component.wings:
                for segment in wing.segments:
                    origin_Z = segment.origin_Z
                    for key in ['le', 'ps', 'ss', 'te']:
                        point_ids[key] = []
                        xs, ys = segment.points['le']
                        for x, y in zip(xs, ys):
                            file.write(f"#{idx} = CARTESIAN_POINT ( 'NONE',  ( {x}, {y}, {origin_Z} ) );\n")
                            point_ids[key].append(idx)
                            idx += 1

                    # Splajny
                    spline_ids = {}
                    for key in ['le', 'ps', 'ss', 'te']:
                        pts = ", ".join(f"#{pid}" for pid in point_ids[key])
                        file.write(f"#{idx} = B_SPLINE_CURVE_WITH_KNOTS ( 'NONE', 3, ( {pts} ), .UNSPECIFIED., .F., .F., ( 4, 4 ), ( 0.0, 1.0 ), .UNSPECIFIED. ) ;\n")
                        spline_ids[key] = idx
                        idx += 1

                    # Wierzchołki (początek i koniec każdego splajnu)
                    vertex_ids = []
                    for key in ['le', 'ps', 'ss', 'te']:
                        for i in [0, -1]:
                            file.write(f"#{idx} = VERTEX_POINT ( 'NONE', #{point_ids[key][i]} ) ;\n")
                            vertex_ids.append(idx)
                            idx += 1

                    # Krawędzie (EDGE_CURVE + ORIENTED_EDGE)
                    edge_ids = []
                    for i, key in enumerate(['le', 'ps', 'ss', 'te']):
                        v_start = vertex_ids[2*i]
                        v_end = vertex_ids[2*i+1]
                        spline = spline_ids[key]
                        file.write(f"#{idx} = EDGE_CURVE ( 'NONE', #{v_start}, #{v_end}, #{spline}, .T. ) ;\n")
                        edge_ids.append(idx)
                        idx += 1
                        file.write(f"#{idx} = ORIENTED_EDGE ( 'NONE', *, *, #{idx-1}, .T. ) ;\n")
                        edge_ids[-1] = idx  # zamieniamy na ORIENTED_EDGE id
                        idx += 1

                        # EDGE_LOOP
                        edge_loop = ", ".join(f"#{eid}" for eid in edge_ids)
                        file.write(f"#{idx} = EDGE_LOOP ( 'NONE', ( {edge_loop} ) ) ;\n")
                        edge_loop_id = idx
                        idx += 1

        # FACE_OUTER_BOUND
        file.write(f"#{idx} = FACE_OUTER_BOUND ( 'NONE', #{edge_loop_id}, .T. ) ;\n")
        face_bound_id = idx
        idx += 1

        # B_SPLINE_SURFACE_WITH_KNOTS (siatka 4xN)
        # Przyjmujemy, że splines to 4 listy po N punktów (le, ps, ss, te)
        N = len(point_ids['le'])
        surf_rows = []
        for i in range(N):
            row = ", ".join(f"#{point_ids[key][i]}" for key in ['le', 'ps', 'ss', 'te'])
            surf_rows.append(f"( {row} )")
        surf_points = ",\n ".join(surf_rows)
        file.write(f"#{idx} = B_SPLINE_SURFACE_WITH_KNOTS ( 'NONE', 3, 3, ( \n {surf_points} ), .UNSPECIFIED., .F., .F., .F., ( 4, 4 ), ( 4, 4 ), ( 0.0, 1.0 ), ( 0.0, 1.0 ), .UNSPECIFIED. ) ;\n")
        surf_id = idx
        idx += 1

        # ADVANCED_FACE
        file.write(f"#{idx} = ADVANCED_FACE ( 'NONE', ( #{face_bound_id} ), #{surf_id}, .T. ) ;\n")
        adv_face_id = idx
        idx += 1

        # OPEN_SHELL
        file.write(f"#{idx} = OPEN_SHELL ( 'NONE', ( #{adv_face_id} ) ) ;\n")
        shell_id = idx
        idx += 1

        # SHELL_BASED_SURFACE_MODEL
        file.write(f"#{idx} = SHELL_BASED_SURFACE_MODEL ( 'NONE', ( #{shell_id} ) );\n")
        sbsm_id = idx
        idx += 1

        # AXIS2_PLACEMENT_3D (origin, Z, X directions)
        file.write(f"#{idx} = CARTESIAN_POINT ( 'NONE',  ( 0.0, 0.0, 0.0 ) );\n")
        axis_origin_id = idx
        idx += 1
        file.write(f"#{idx} = DIRECTION ( 'NONE',  ( 0.0, 0.0, 1.0 ) );\n")
        axis_z_id = idx
        idx += 1
        file.write(f"#{idx} = DIRECTION ( 'NONE',  ( 1.0, 0.0, 0.0 ) );\n")
        axis_x_id = idx
        idx += 1
        file.write(f"#{idx} = AXIS2_PLACEMENT_3D ( 'NONE', #{axis_origin_id}, #{axis_z_id}, #{axis_x_id} );\n")
        axis2placement_id = idx
        idx += 1

        # APPLICATION_CONTEXT
        file.write(f"#{idx} = APPLICATION_CONTEXT ( 'configuration controlled 3d designs of mechanical parts and assemblies' );\n")
        app_ctx_id = idx
        idx += 1

        # MECHANICAL_CONTEXT
        file.write(f"#{idx} = MECHANICAL_CONTEXT ( 'NONE', #{app_ctx_id}, 'mechanical' );\n")
        mech_ctx_id = idx
        idx += 1

        # PRODUCT
        file.write(f"#{idx} = PRODUCT ( 'AirFLOW', 'AirFLOW', '', ( #{mech_ctx_id} ) );\n")
        product_id = idx
        idx += 1

        # PRODUCT_DEFINITION_FORMATION
        file.write(f"#{idx} = PRODUCT_DEFINITION_FORMATION ( '1', '', #{product_id} );\n")
        pdf_id = idx
        idx += 1

        # DESIGN_CONTEXT
        file.write(f"#{idx} = DESIGN_CONTEXT ( 'detailed design', #{app_ctx_id}, 'design' );\n")
        design_ctx_id = idx
        idx += 1

        # PRODUCT_DEFINITION
        file.write(f"#{idx} = PRODUCT_DEFINITION ( 'NONE', '', #{pdf_id}, #{design_ctx_id} );\n")
        pd_id = idx
        idx += 1

        # PRODUCT_DEFINITION_SHAPE
        file.write(f"#{idx} = PRODUCT_DEFINITION_SHAPE ( 'NONE', '', #{pd_id} );\n")
        pds_id = idx
        idx += 1

        # MANIFOLD_SURFACE_SHAPE_REPRESENTATION (nazwa, model, axis2placement, kontekst)
        file.write(f"#{idx} = MANIFOLD_SURFACE_SHAPE_REPRESENTATION ( 'AirFLOW', ( #{sbsm_id}, #{axis2placement_id} ), #{idx+1} );\n")
        mssr_id = idx
        idx += 1

        # units, uncertainty, context
        idx, geom_ctx_id = units(file, idx)

        # SHAPE_DEFINITION_REPRESENTATION
        file.write(f"#{idx} = SHAPE_DEFINITION_REPRESENTATION ( #{pds_id}, #{mssr_id} );\n")
        sdr_id = idx
        idx += 1

        # PRODUCT_RELATED_PRODUCT_CATEGORY
        file.write(f"#{idx} = PRODUCT_RELATED_PRODUCT_CATEGORY ( 'detail', '', ( #{product_id} ) );\n")
        idx += 1

        # APPLICATION_PROTOCOL_DEFINITION
        file.write(f"#{idx} = APPLICATION_PROTOCOL_DEFINITION ( 'international standard', 'config_control_design', 1994, #{app_ctx_id} );\n")
        idx += 1

        FOOTER(file)

if __name__ == "__main__":
    with open("file.step", "w") as file:
        HEADER(file)
        ENDSEC_OPEN(file)

        FOOTER(file)