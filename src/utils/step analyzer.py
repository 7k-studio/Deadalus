# Deep analysis of /mnt/data/test9.step
import re, json, math
from collections import defaultdict, OrderedDict

path = "test6_from_solid.step"
with open(path, "r") as f:
    txt = f.read()

# Extract entity definitions: lines starting with #id = ... ;
entity_pattern = re.compile(r'(?m)^(#\d+)\s*=\s*([^;]+);')
entities = OrderedDict(entity_pattern.findall(txt))

defined_ids = set(entities.keys())

# Helper to extract uppercase entity type from RHS
def entity_type(rhs):
    m = re.match(r'\s*([A-Z0-9_]+)\s*\(', rhs.strip())
    return m.group(1) if m else None

# Build type -> ids map and rhs map
type_map = defaultdict(list)
for id_, rhs in entities.items():
    t = entity_type(rhs) or "UNKNOWN"
    type_map[t].append(id_)

# Utility: find all referenced ids in a RHS
ref_pattern = re.compile(r'(#\d+)')
def refs(rhs):
    return ref_pattern.findall(rhs)

# Parse Cartesian points coordinates
cart_points = {}
cp_pattern = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([^\)]+)\s*\)\s*\)", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "CARTESIAN_POINT":
        m = cp_pattern.search(rhs)
        if m:
            nums = [float(n.strip()) for n in m.group(1).split(',')]
            cart_points[id_] = nums

# Parse VERTEX_POINT -> maps vertex id to cartesian point id (or coordinates)
vertex_point = {}
vp_pattern = re.compile(r"VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*(#[0-9]+)\s*\)", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "VERTEX_POINT":
        m = vp_pattern.search(rhs)
        if m:
            vertex_point[id_] = m.group(1)

# Parse EDGE_CURVE -> vertex start, vertex end, curve ref
edge_curve = {}
ec_pattern = re.compile(r"EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*(#[0-9]+)\s*,\s*(#[0-9]+)\s*,\s*(#[0-9]+)\s*,", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "EDGE_CURVE":
        m = ec_pattern.search(rhs)
        if m:
            edge_curve[id_] = {"v1": m.group(1), "v2": m.group(2), "curve": m.group(3)}

# Parse ORIENTED_EDGE -> gives underlying edge id
oriented_edge = {}
oe_pattern = re.compile(r"ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*[^,]*,\s*[^,]*,\s*(#[0-9]+)\s*,\s*\.(T|F)\.", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "ORIENTED_EDGE":
        m = oe_pattern.search(rhs)
        if m:
            oriented_edge[id_] = {"edge": m.group(1), "sense": m.group(2)}

# Parse EDGE_LOOP -> list of oriented edges
edge_loop = {}
el_pattern = re.compile(r"EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(\s*([^\)]+)\s*\)\s*\)", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "EDGE_LOOP":
        m = el_pattern.search(rhs)
        if m:
            ids = re.findall(r'(#\d+)', m.group(1))
            edge_loop[id_] = ids

# Parse FACE_OUTER_BOUND -> loop id
face_outer = {}
fob_pattern = re.compile(r"FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*(#[0-9]+)\s*,\s*\.(T|F)\.", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "FACE_OUTER_BOUND":
        m = fob_pattern.search(rhs)
        if m:
            face_outer[id_] = {"loop": m.group(1), "sense": m.group(2)}

# Parse ADVANCED_FACE -> bounds list and surface id
adv_face = {}
af_pattern = re.compile(r"ADVANCED_FACE\s*\(\s*'[^']*'\s*,\s*\(\s*([^\)]*)\)\s*,\s*(#[0-9]+)\s*,\s*\.(T|F)\.", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "ADVANCED_FACE":
        m = af_pattern.search(rhs)
        if m:
            bounds_list = re.findall(r'(#\d+)', m.group(1))
            surface = m.group(2)
            adv_face[id_] = {"bounds": bounds_list, "surface": surface}

# Parse OPEN_SHELL / SHELL_BASED_SURFACE_MODEL references
open_shell = {}
os_pattern = re.compile(r"OPEN_SHELL\s*\(\s*'([^']*)'\s*,\s*\(\s*([^\)]*)\)\s*\)", re.IGNORECASE)
for id_, rhs in entities.items():
    if entity_type(rhs) == "OPEN_SHELL":
        m = os_pattern.search(rhs)
        if m:
            faces = re.findall(r'(#\d+)', m.group(2))
            open_shell[id_] = {"name": m.group(1), "faces": faces}

# Parse SHELL_BASED_SURFACE_MODEL -> list of shells
sbs_pattern = re.compile(r"SHELL_BASED_SURFACE_MODEL\s*\(\s*'[^']*'\s*,\s*\(\s*([^\)]*)\)\s*\)", re.IGNORECASE)
shell_based = {}
for id_, rhs in entities.items():
    if entity_type(rhs) == "SHELL_BASED_SURFACE_MODEL":
        m = sbs_pattern.search(rhs)
        if m:
            shells = re.findall(r'(#\d+)', m.group(1))
            shell_based[id_] = shells

# Parse SHAPE_REPRESENTATION / MANIFOLD_SURFACE_SHAPE_REPRESENTATION
shape_repr = {}
sr_pattern = re.compile(r"([A-Z_]+)\s*\(\s*'[^']*'\s*,\s*\(\s*([^\)]*)\)\s*,\s*(#[0-9]+)\s*\)", re.IGNORECASE)
for id_, rhs in entities.items():
    t = entity_type(rhs)
    if t and ("SHAPE_REPRESENTATION" in t or "MANIFOLD" in t or "GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION" in t):
        m = sr_pattern.search(rhs)
        if m:
            items = re.findall(r'(#\d+)', m.group(2))
            shape_repr[id_] = {"type": m.group(1), "items": items, "context": m.group(3)}

# Parse PRODUCT / PRODUCT_DEFINITION_SHAPE / SHAPE_DEFINITION_REPRESENTATION mapping
product_defs = {}
for id_, rhs in entities.items():
    t = entity_type(rhs)
    if t in ("PRODUCT_DEFINITION_SHAPE","SHAPE_DEFINITION_REPRESENTATION","PRODUCT","PRODUCT_DEFINITION"):
        product_defs[id_] = rhs

# Collect all referenced ids
all_refs = set()
for rhs in entities.values():
    all_refs.update(refs(rhs))

# Missing references
missing_refs = sorted(list(all_refs - defined_ids))

# For each ADVANCED_FACE, try to collect cartesian points by walking bounds->loops->oriented_edges->edge_curve->vertex_point->cartesian_point
def collect_face_points(face_id):
    pts = []
    info = {"face": face_id, "bounds": [], "edges": [], "points": []}
    face = adv_face.get(face_id)
    if not face:
        return info
    for bound_id in face["bounds"]:
        info["bounds"].append(bound_id)
        loop = edge_loop.get(bound_id)
        if not loop:
            # maybe bound references FACE_OUTER_BOUND id which maps to loop
            fob = entities.get(bound_id)
            if fob and "FACE_OUTER_BOUND" in fob:
                m = fob_pattern.search(fob)
                if m:
                    loop_id = m.group(1)
                    loop = edge_loop.get(loop_id)
                    # record that
                    info["edges"].append({"bound": bound_id, "loop": loop_id, "oriented_edges": loop})
        else:
            # direct loop found (rare)
            info["edges"].append({"bound": bound_id, "loop": bound_id, "oriented_edges": loop})
        # Now if we have oriented edges, traverse
        oriented_ids = None
        if loop:
            oriented_ids = loop
            for oe in oriented_ids:
                edge_info = oriented_edge.get(oe)
                if not edge_info:
                    # sometimes oriented edges call with different formatting, try to extract underlying edge id from entity text
                    oe_rhs = entities.get(oe, "")
                    m2 = re.search(r",\s*(#[0-9]+)\s*,\s*\.(T|F)\.", oe_rhs)
                    if m2:
                        underlying_edge = m2.group(1)
                        edge_info = {"edge": underlying_edge, "sense": m2.group(2)}
                if edge_info:
                    ecurve = edge_curve.get(edge_info["edge"])
                    if ecurve:
                        info["edges"].append({"oriented_edge": oe, "edge_curve": edge_info["edge"], "v1": ecurve["v1"], "v2": ecurve["v2"], "curve": ecurve["curve"]})
                        # vertex_point maps to cartesian points
                        v1_cp = vertex_point.get(ecurve["v1"])
                        v2_cp = vertex_point.get(ecurve["v2"])
                        if v1_cp and v1_cp in cart_points:
                            pts.append(cart_points[v1_cp])
                        if v2_cp and v2_cp in cart_points:
                            pts.append(cart_points[v2_cp])
    # Deduplicate points
    unique_pts = []
    seen = set()
    for p in pts:
        tup = tuple(round(x,9) for x in p)
        if tup not in seen:
            seen.add(tup)
            unique_pts.append(p)
    info["points"] = unique_pts
    return info

# Build face reports
face_reports = {}
for fid in adv_face.keys():
    face_reports[fid] = collect_face_points(fid)
    # Compute bbox
    pts = face_reports[fid]["points"]
    if pts:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        face_reports[fid]["bbox"] = {"xmin":min(xs),"xmax":max(xs),"ymin":min(ys),"ymax":max(ys),"zmin":min(zs),"zmax":max(zs)}
    else:
        face_reports[fid]["bbox"] = None

# Also produce mapping shell->faces and top-level shape def mapping
shells = {sid: shell_based[sid] for sid in shell_based}
open_shells = open_shell

# Count of B_SPLINE_SURFACE_WITH_KNOTS and referenced cart points
bsurf_refs = {}
for id_ in type_map.get("B_SPLINE_SURFACE_WITH_KNOTS", []):
    brefs = refs(entities[id_])
    # intersection with cart_points keys
    ctrl_pts = [r for r in brefs if r in cart_points]
    bsurf_refs[id_] = {"refs_total": len(brefs), "ctrl_pts_found": len(ctrl_pts), "ctrl_pts": ctrl_pts[:8]}

# Summary output
summary = {
    "file": path,
    "total_entities": len(entities),
    "defined_ids_sample": list(defined_ids)[:10],
    "entity_type_counts": {k: len(v) for k,v in type_map.items()},
    "shape_representations": shape_repr,
    "shell_based_surface_models": shell_based,
    "open_shells": open_shell,
    "advanced_faces_count": len(adv_face),
    "advanced_faces": adv_face,
    "face_reports_summary": {fid: {"num_bounds": len(v["bounds"]), "num_points": len(face_reports[fid]["points"]), "bbox": face_reports[fid]["bbox"]} for fid,v in adv_face.items()},
    "missing_references_count": len(missing_refs),
    "missing_references_sample": missing_refs[:20],
    "b_spline_surface_summary": bsurf_refs
}

# Print a readable report
print("DEEP ANALYSIS OF:", path)
print("="*70)
print(f"Total entities parsed: {len(entities)}")
print("\nEntity type counts (top entries):")
for t,c in sorted(summary["entity_type_counts"].items(), key=lambda x:-x[1])[:20]:
    print(f"  {t:35s} : {c:4d}")
print("\nShell-based models found:", shell_based)
print("Open shells found:", open_shell)
print("\nTop-level shape representations:")
for sid, info in shape_repr.items():
    print(f"  {sid} : {info['type']} with items {info['items']} context {info['context']}")

print("\nAdvanced faces and their surfaces:")
for fid, info in adv_face.items():
    pts = face_reports[fid]["points"]
    print(f"  {fid}: surface {info['surface']}, bounds {info['bounds']}, points found {len(pts)}")

print("\nSummary of face point bboxes:")
for fid, rep in face_reports.items():
    print(f"  {fid}: num_points={len(rep['points'])}, bbox={rep['bbox']}")

print("\nMissing referenced IDs (count={}):".format(len(missing_refs)))
if missing_refs:
    print("  " + ", ".join(missing_refs[:50]))
else:
    print("  None")

# Final structured JSON for examination if needed
print("\n\nStructured summary (JSON):\n")
print(json.dumps(summary, indent=2))

# Also save the summary to file for download if desired
with open(f"{path}_deep_summary.json","w") as f:
    f.write(json.dumps(summary, indent=2))

f"{path}_deep_summary.json"
