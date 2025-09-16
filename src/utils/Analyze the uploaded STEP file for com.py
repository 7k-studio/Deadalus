# Analyze the uploaded STEP file for common geometry issues without requiring OCC.
# We'll parse the STEP file text to extract points, vertices, and edges,
# compute a bounding box, find extremely small or zero-length edges,
# detect duplicate coincident vertices, and list entities counts.

# Deep-dive analysis of /mnt/data/o.step for topology issues that commonly break CAD imports.
# This does not require OpenCascade: we parse STEP text and check for:
# - Open vs non-manifold edges (edge usage counts across faces)
# - Loop continuity (do oriented edges connect head-to-tail?)
# - Duplicate/coincident vertices
# - Planarity violations for faces that declare a PLANE surface
# - Basic size/units, entity counts
#
# Results are displayed as dataframes and a JSON summary is saved for download.

import re, math, json
from collections import defaultdict, Counter
import pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Units (rough inference)
if re.search(r"MILLIMETRE", s, re.I):
    units = "millimetre"
elif re.search(r"INCH", s, re.I):
    units = "inch"
elif re.search(r"METRE|METER", s, re.I):
    units = "metre"
else:
    units = "unknown"
unit_scale_mm = {"inch":25.4,"millimetre":1.0,"metre":1000.0}.get(units,1.0)

# Entities
entity_counts = defaultdict(int)
for ent in re.finditer(r"#\d+\s*=\s*([A-Z0-9_]+)\s*\(", s, re.I):
    entity_counts[ent.group(1).upper()] += 1

# Points and vertices
pt_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<xyz>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)
points = {}
for m in pt_re.finditer(s):
    pid = int(m.group("id"))
    xyz = [float(x.strip()) for x in m.group("xyz").split(",")]
    while len(xyz)<3: xyz.append(0.0)
    points[pid] = tuple(xyz[:3])

vtx_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.I)
vertex_to_point = {}
for m in vtx_re.finditer(s):
    vid = int(m.group("id")); pid = int(m.group("pid"))
    if pid in points:
        vertex_to_point[vid]=points[pid]

# Edges
edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges = {}
for m in edge_re.finditer(s):
    eid=int(m.group("id")); v1=int(m.group("v1")); v2=int(m.group("v2")); curve=int(m.group("curve")); sense=m.group("sense").upper()=="T"
    p1 = vertex_to_point.get(v1); p2 = vertex_to_point.get(v2)
    length = math.dist(p1,p2) if p1 and p2 else None
    edges[eid]={"v1":v1,"v2":v2,"p1":p1,"p2":p2,"length":length,"curve":curve,"sense":sense}

# Oriented edges
oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\$,\s*\$,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
oriented_edges={}
for m in oedge_re.finditer(s):
    oid=int(m.group("id")); rid=int(m.group("edge")); osense=m.group("sense").upper()=="T"
    oriented_edges[oid]={"edge":rid,"sense":osense}

# Edge Loops and Face bounds -> loops
loop_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.DOTALL)
edge_loops={}
for m in loop_re.finditer(s):
    lid=int(m.group("id"))
    items = [int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]
    edge_loops[lid]=items

fob_re = re.compile(r"#(?P<id>\d+)\s*=\s*FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*#(?P<loop>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
face_outer_bound={}
for m in fob_re.finditer(s):
    fid=int(m.group("id")); lid=int(m.group("loop")); sense=m.group("sense").upper()=="T"
    face_outer_bound[fid]={"loop":lid,"sense":sense}

# Faces (ADVANCED_FACE -> bounds and surface)
face_re = re.compile(r"#(?P<id>\d+)\s*=\s*ADVANCED_FACE\s*\(\s*\((?P<bounds>[^)]*)\)\s*,\s*#(?P<surf>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I|re.DOTALL)
faces={}
for m in face_re.finditer(s):
    fid=int(m.group("id"))
    btxt=m.group("bounds")
    bounds = [int(i.strip().lstrip("#")) for i in btxt.replace("\n"," ").split(",") if i.strip().startswith("#")]
    surf=int(m.group("surf"))
    sense=m.group("sense").upper()=="T"
    faces[fid]={"bounds":bounds,"surface":surf,"sense":sense}

# Map planes (optional planarity check)
plane_re = re.compile(r"#(?P<id>\d+)\s*=\s*PLANE\s*\(\s*'[^']*'\s*,\s*#(?P<ax>\d+)\s*\)\s*;", re.I)
axis_re = re.compile(r"#(?P<id>\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(?P<p>\d+)\s*,\s*#(?P<z>\d+)\s*,\s*#(?P<x>\d+)\s*\)\s*;", re.I)
dir_re = re.compile(r"#(?P<id>\d+)\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<d>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)

dir_map = {}
for m in dir_re.finditer(s):
    did=int(m.group("id"))
    d = [float(x.strip()) for x in m.group("d").split(",")]
    while len(d)<3: d.append(0.0)
    dir_map[did]=tuple(d[:3])

axis_map = {}
for m in axis_re.finditer(s):
    aid=int(m.group("id")); p=int(m.group("p")); z=int(m.group("z")); x=int(m.group("x"))
    axis_map[aid]={"p":p,"z":z,"x":x}

plane_map = {}
for m in plane_re.finditer(s):
    pid=int(m.group("id")); ax=int(m.group("ax")); axis=axis_map.get(ax)
    plane_map[pid]={"axis":axis}

# Helper: distance point to plane
def point_plane_dist(p, origin, normal):
    # normal need not be unit; we normalize
    nx,ny,nz = normal
    nn = math.sqrt(nx*nx+ny*ny+nz*nz) or 1.0
    nx/=nn; ny/=nn; nz/=nn
    ox,oy,oz = origin
    return abs((p[0]-ox)*nx + (p[1]-oy)*ny + (p[2]-oz)*nz)

# Build face -> loop continuity and edge usage
edge_usage = Counter()   # undirected usage across all faces
nonmanifold = []         # edges used >2 times
boundary_edges = []      # edges used only once
loop_problems = []       # gaps or mismatched continuity
repeat_vertices_in_loop = []

def undirected_key(eid):
    e = edges.get(eid)
    if not e: return None
    v1,v2 = e["v1"], e["v2"]
    return tuple(sorted((v1,v2)))

# Collect all vertices per face for planarity check
face_vertices = defaultdict(list)

for fid, f in faces.items():
    for bid in f["bounds"]:
        lb = face_outer_bound.get(bid)
        if not lb: continue
        lid = lb["loop"]
        oids = edge_loops.get(lid, [])
        # continuity: simulate walking
        prev_tail = None
        loop_vertex_ids = []
        for oid in oids:
            oe = oriented_edges.get(oid)
            if not oe: 
                loop_problems.append({"face":fid,"loop":lid,"issue":"oriented_edge_missing","oriented_edge":oid})
                continue
            eid = oe["edge"]
            e = edges.get(eid)
            if not e:
                loop_problems.append({"face":fid,"loop":lid,"issue":"edge_missing","edge":eid})
                continue
            # Determine direction
            forward = oe["sense"]  # True means as EDGE_CURVE orientation
            start = e["v1"] if forward else e["v2"]
            end   = e["v2"] if forward else e["v1"]
            # continuity check
            if prev_tail is not None and start != prev_tail:
                loop_problems.append({"face":fid,"loop":lid,"issue":"loop_gap_or_order","expected":prev_tail,"got":start,"oriented_edge":oid,"edge":eid})
            prev_tail = end
            loop_vertex_ids.append(start)
            face_vertices[fid].append(start)
            # track usage (undirected)
            k = undirected_key(eid)
            if k: edge_usage[k]+=1
        # also add last vertex for closure check
        if prev_tail is not None:
            loop_vertex_ids.append(prev_tail)
            if loop_vertex_ids[0] != loop_vertex_ids[-1]:
                loop_problems.append({"face":fid,"loop":lid,"issue":"loop_not_closed","start":loop_vertex_ids[0],"end":loop_vertex_ids[-1]})
        # repeated vertex IDs inside the loop (self-touch)
        counts = Counter(loop_vertex_ids)
        repeats = [v for v,c in counts.items() if c>2]  # >2 times indicates likely self-intersection or bow-tie
        if repeats:
            repeat_vertices_in_loop.append({"face":fid,"loop":lid,"vertex_ids":repeats,"counts":[counts[v] for v in repeats]})

# Classify edges by usage
for (v1,v2), c in edge_usage.items():
    if c==1:
        boundary_edges.append({"v1":v1,"v2":v2,"usage":c})
    elif c>2:
        nonmanifold.append({"v1":v1,"v2":v2,"usage":c})

# Build tiny/short edge list
tiny_mm = 1e-3
short_mm = 0.05
tiny_edges = []
short_edges = []
for eid,e in edges.items():
    if e["length"] is None: continue
    Lmm = e["length"]*unit_scale_mm
    if Lmm <= tiny_mm:
        tiny_edges.append({"edge_id":eid,"v1":e["v1"],"v2":e["v2"],"length_mm":Lmm})
    elif Lmm <= short_mm:
        short_edges.append({"edge_id":eid,"v1":e["v1"],"v2":e["v2"],"length_mm":Lmm})

# Duplicate vertices (coincident) within tight tol
tol_mm = 1e-4
tol_units = tol_mm/unit_scale_mm if unit_scale_mm else tol_mm
bins=defaultdict(list)
for vid,p in vertex_to_point.items():
    key=(round(p[0]/tol_units), round(p[1]/tol_units), round(p[2]/tol_units))
    bins[key].append((vid,p))
coincident_groups=[items for items in bins.values() if len(items)>1]

# Compute bbox
coords = [p for p in vertex_to_point.values()]
bbox=None
if coords:
    xs=[c[0] for c in coords]; ys=[c[1] for c in coords]; zs=[c[2] for c in coords]
    bbox={"xmin":min(xs),"xmax":max(xs),"ymin":min(ys),"ymax":max(ys),"zmin":min(zs),"zmax":max(zs),
          "dx":max(xs)-min(xs),"dy":max(ys)-min(ys),"dz":max(zs)-min(zs)}

# Planarity checks for faces with PLANE surface
# For each face, if its surface id is a PLANE, get axis origin+normal and measure max deviation of its vertices
# We need axis origin: AXIS2_PLACEMENT_3D -> point (cartesian) for origin, z direction id for normal.
# Map placements to origin+normal
origin_map = {}
for aid,ax in axis_map.items():
    ppid = ax["p"]; zdid = ax["z"]
    origin = points.get(ppid)
    normal = dir_map.get(zdid)
    if origin and normal:
        origin_map[aid]={"origin":origin,"normal":normal}

plane_face_deviations=[]
for fid,f in faces.items():
    sid = f["surface"]
    if sid in plane_map:
        axis = plane_map[sid]["axis"]
        if not axis or axis["p"] not in points or axis["z"] not in dir_map: 
            continue
        origin = points.get(axis["p"]); normal = dir_map.get(axis["z"])
        verts = [vertex_to_point.get(vid) for vid in set(face_vertices[fid]) if vid in vertex_to_point]
        if not verts: continue
        dists = [point_plane_dist(p, origin, normal) for p in verts]
        maxd = max(dists)
        plane_face_deviations.append({"face":fid,"surface":sid,"max_abs_distance_units":maxd, "max_abs_distance_mm":maxd*unit_scale_mm, "num_vertices":len(verts)})

# Edge-face usage per edge id (optional detailed view)
edge_face_usage = defaultdict(int)
# Count how many face loops reference each underlying edge (undirected)
for fid,f in faces.items():
    for bid in f["bounds"]:
        lid = face_outer_bound.get(bid,{}).get("loop")
        if not lid: continue
        for oid in edge_loops.get(lid,[]):
            oe = oriented_edges.get(oid)
            if not oe: continue
            eid = oe["edge"]
            # count directed usage too
            edge_face_usage[eid]+=1

# DataFrames for presentation
df_entities = pd.DataFrame(sorted(entity_counts.items()), columns=["Entity","Count"])
df_tiny = pd.DataFrame(tiny_edges)
df_short = pd.DataFrame(short_edges)
df_nonmanifold = pd.DataFrame(nonmanifold)
df_boundary = pd.DataFrame(boundary_edges)
df_loop_issues = pd.DataFrame(loop_problems)
df_repeat_vtx = pd.DataFrame(repeat_vertices_in_loop)
df_planes = pd.DataFrame(plane_face_deviations).sort_values("max_abs_distance_mm", ascending=False) if plane_face_deviations else pd.DataFrame()
df_edge_usage = pd.DataFrame([{"edge_id":eid,"directed_face_refs":cnt,"length":edges[eid]["length"]} for eid,cnt in edge_face_usage.items()])

'''
display_dataframe_to_user("Entity Counts (o.step)", df_entities)
if not df_boundary.empty: display_dataframe_to_user("Boundary Edges (used by exactly 1 face loop)", df_boundary)
if not df_nonmanifold.empty: display_dataframe_to_user("Non-manifold Edges (used by >2 face loops)", df_nonmanifold)
if not df_loop_issues.empty: display_dataframe_to_user("Loop Continuity Issues", df_loop_issues)
if not df_repeat_vtx.empty: display_dataframe_to_user("Loops with Repeated Vertices (likely self-touch)", df_repeat_vtx)
if not df_tiny.empty: display_dataframe_to_user("Degenerate Edges (≈0 length)", df_tiny)
if not df_short.empty: display_dataframe_to_user("Suspiciously Short Edges", df_short)
if not df_planes.empty: display_dataframe_to_user("Planar Face Deviations", df_planes)
if not df_edge_usage.empty: display_dataframe_to_user("Edge Usage per Face (directed refs)", df_edge_usage)
'''

summary = {
    "units": units,
    "bbox": bbox,
    "counts": dict(entity_counts),
    "num_vertices": len(vertex_to_point),
    "num_edges": len(edges),
    "num_faces": len(faces),
    "num_boundary_edges": len(boundary_edges),
    "num_nonmanifold_edges": len(nonmanifold),
    "num_loop_issues": len(loop_problems),
    "num_loops_with_repeats": len(df_repeat_vtx),
    "num_tiny_edges": len(tiny_edges),
    "num_short_edges": len(short_edges),
    "num_coincident_vertex_groups": len(coincident_groups),
    "planar_deviation_max_mm": max((r["max_abs_distance_mm"] for r in plane_face_deviations), default=0.0),
}
report_path = "o_step_diagnostics.json"
with open(report_path,"w") as f:
    json.dump(summary, f, indent=2)

summary, f"Saved report to {report_path}"



import re
import math
import json
import pandas as pd
from collections import defaultdict
#from IPython.display import display
#

path = "o.step"

with open(path, "r", errors="ignore") as f:
    step_text = f.read()

header_match = re.search(r"HEADER;(.*?)ENDSEC;", step_text, flags=re.DOTALL|re.IGNORECASE)
header_text = header_match.group(1) if header_match else ""

# Infer units by simple keyword search
units = None
if re.search(r"MILLIMETRE", step_text, flags=re.IGNORECASE):
    units = "millimetre"
elif re.search(r"INCH", step_text, flags=re.IGNORECASE):
    units = "inch"
elif re.search(r"METRE|METER", step_text, flags=re.IGNORECASE):
    units = "metre"
else:
    units = "unknown"

# Parse CARTESIAN_POINT
point_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<x>[-+Ee0-9\.\s,]+)\s*\)\s*\)\s*;", re.IGNORECASE)
points = {}
for m in point_re.finditer(step_text):
    pid = int(m.group("id"))
    coords_str = m.group("x").strip()
    vals = [float(v.strip()) for v in coords_str.split(",")[:3]]
    while len(vals) < 3:
        vals.append(0.0)
    points[pid] = tuple(vals[:3])

# Parse VERTEX_POINT -> CARTESIAN_POINT
vertex_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.IGNORECASE)
vertex_to_point = {}
for m in vertex_re.finditer(step_text):
    vid = int(m.group("id"))
    pid = int(m.group("pid"))
    if pid in points:
        vertex_to_point[vid] = points[pid]

# Parse EDGE_CURVE (two vertices)
edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.IGNORECASE)
edges = []
for m in edge_re.finditer(step_text):
    eid = int(m.group("id"))
    v1 = int(m.group("v1"))
    v2 = int(m.group("v2"))
    curve = int(m.group("curve"))
    sense = True if m.group("sense").upper() == "T" else False
    p1 = vertex_to_point.get(v1)
    p2 = vertex_to_point.get(v2)
    length = None
    if p1 and p2:
        length = math.dist(p1, p2)
    edges.append({"edge_id": eid, "v1": v1, "v2": v2, "curve": curve, "sense": sense, "p1": p1, "p2": p2, "length": length})

# Entity counts
entity_counts = defaultdict(int)
for ent in re.finditer(r"#\d+\s*=\s*([A-Z0-9_]+)\s*\(", step_text, re.IGNORECASE):
    entity = ent.group(1).upper()
    entity_counts[entity] += 1

# Bounding box using vertex points (or all points if vertices missing)
coords = list(vertex_to_point.values()) if vertex_to_point else list(points.values())
bbox = None
if coords:
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] for c in coords]
    bbox = {
        "xmin": min(xs), "xmax": max(xs),
        "ymin": min(ys), "ymax": max(ys),
        "zmin": min(zs), "zmax": max(zs),
        "dx": (max(xs) - min(xs)),
        "dy": (max(ys) - min(ys)),
        "dz": (max(zs) - min(zs)),
    }

# Tiny/short edges
unit_scale = {"inch": 25.4, "millimetre": 1.0, "metre": 1000.0}
mm_per_unit = unit_scale.get(units, 1.0)
tiny_threshold_mm = 1e-3
short_threshold_mm = 0.05
tiny_edges = []
short_edges = []
for e in edges:
    if e["length"] is None:
        continue
    length_mm = e["length"] * mm_per_unit
    if length_mm <= tiny_threshold_mm:
        tiny_edges.append({**e, "length_mm": length_mm})
    elif length_mm <= short_threshold_mm:
        short_edges.append({**e, "length_mm": length_mm})

# Coincident vertex groups within tolerance
coincident_groups = []
tol_mm = 1e-4
tol_units = tol_mm / mm_per_unit if mm_per_unit else tol_mm
by_coord = defaultdict(list)
for vid, p in vertex_to_point.items():
    key = (round(p[0]/tol_units), round(p[1]/tol_units), round(p[2]/tol_units))
    by_coord[key].append((vid, p))

for key, items in by_coord.items():
    if len(items) > 1:
        coincident_groups.append(items)

# Points far from origin (unit mix)
far_points = []
if bbox:
    limit_by_unit = {"millimetre": 1e6, "metre": 1e3, "inch": 1e5}
    limit = limit_by_unit.get(units, 1e6)
    for vid, p in vertex_to_point.items():
        r = math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)
        if r > limit:
            far_points.append({"vertex_id": vid, "coord": p, "radius_units": r})

# Prepare DataFrames
counts_df = pd.DataFrame(sorted(entity_counts.items(), key=lambda x: x[0]), columns=["Entity", "Count"])
edges_df = pd.DataFrame(edges)
tiny_df = pd.DataFrame(tiny_edges)
short_df = pd.DataFrame(short_edges)
far_df = pd.DataFrame(far_points)

# Display to user
#display("STEP Entity Counts", counts_df)
#if not edges_df.empty:
#    display("All Edges (with computed lengths where possible)", edges_df[["edge_id","v1","v2","length"]])
#if not tiny_df.empty:
#    display("Degenerate (≈0) Edges", tiny_df[["edge_id","v1","v2","length_mm"]])
#if not short_df.empty:
#    display("Suspiciously Short Edges", short_df[["edge_id","v1","v2","length_mm"]])
#if not far_df.empty:
#    display("Points Far From Origin", far_df)

summary = {
    "units_inferred": units,
    "bbox": bbox,
    "num_points": len(points),
    "num_vertices": len(vertex_to_point),
    "num_edges": len(edges),
    "num_tiny_edges": len(tiny_edges),
    "num_short_edges": len(short_edges),
    "num_coincident_vertex_groups": len(coincident_groups),
    "coincident_groups_sample": [
        {"vertex_ids": [vid for vid,_ in grp], "coord": grp[0][1]} for grp in coincident_groups[:20]
    ],
    "entity_counts_top": sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:20],
    "header_excerpt": header_text[:1000],
}
report_path = "step_geometry_report.json"
with open(report_path, "w") as f:
    json.dump(summary, f, indent=2)

summary, f"Report saved to {report_path}"

# Re-run after kernel reset to produce diagnostics and tables.
import re, math, json
from collections import defaultdict, Counter
import pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Units
if re.search(r"MILLIMETRE", s, re.I):
    units = "millimetre"
elif re.search(r"INCH", s, re.I):
    units = "inch"
elif re.search(r"METRE|METER", s, re.I):
    units = "metre"
else:
    units = "unknown"
unit_scale_mm = {"inch":25.4,"millimetre":1.0,"metre":1000.0}.get(units,1.0)

# Entities
entity_counts = defaultdict(int)
for ent in re.finditer(r"#\d+\s*=\s*([A-Z0-9_]+)\s*\(", s, re.I):
    entity_counts[ent.group(1).upper()] += 1

# Points & vertices
pt_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<xyz>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)
points={}
for m in pt_re.finditer(s):
    pid=int(m.group("id")); xyz=[float(x) for x in m.group("xyz").split(",")]
    while len(xyz)<3: xyz.append(0.0)
    points[pid]=tuple(xyz[:3])

vtx_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.I)
vertex_to_point={}
for m in vtx_re.finditer(s):
    vid=int(m.group("id")); pid=int(m.group("pid"))
    if pid in points: vertex_to_point[vid]=points[pid]

# Edges
edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges={}
for m in edge_re.finditer(s):
    eid=int(m.group("id")); v1=int(m.group("v1")); v2=int(m.group("v2"))
    curve=int(m.group("curve")); sense=m.group("sense").upper()=="T"
    p1=vertex_to_point.get(v1); p2=vertex_to_point.get(v2)
    length = ( ( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2 ) **0.5 ) if p1 and p2 else None
    edges[eid]={"v1":v1,"v2":v2,"p1":p1,"p2":p2,"length":length,"curve":curve,"sense":sense}

# Oriented edges, loops, face bounds, faces
oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\$,\s*\$,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
oriented_edges={}
for m in oedge_re.finditer(s):
    oriented_edges[int(m.group("id"))]={"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"}

loop_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
edge_loops={}
for m in loop_re.finditer(s):
    lid=int(m.group("id"))
    items=[int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]
    edge_loops[lid]=items

fob_re = re.compile(r"#(?P<id>\d+)\s*=\s*FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*#(?P<loop>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
face_outer_bound={}
for m in fob_re.finditer(s):
    face_outer_bound[int(m.group("id"))]={"loop":int(m.group("loop")),"sense":m.group("sense").upper()=="T"}

face_re = re.compile(r"#(?P<id>\d+)\s*=\s*ADVANCED_FACE\s*\(\s*\((?P<bounds>[^)]*)\)\s*,\s*#(?P<surf>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I|re.S)
faces={}
for m in face_re.finditer(s):
    fid=int(m.group("id"))
    bounds=[int(i.strip().lstrip("#")) for i in m.group("bounds").replace("\n"," ").split(",") if i.strip().startswith("#")]
    faces[fid]={"bounds":bounds,"surface":int(m.group("surf")),"sense":m.group("sense").upper()=="T"}

# Planes (for planarity check)
plane_re = re.compile(r"#(?P<id>\d+)\s*=\s*PLANE\s*\(\s*'[^']*'\s*,\s*#(?P<ax>\d+)\s*\)\s*;", re.I)
axis_re = re.compile(r"#(?P<id>\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(?P<p>\d+)\s*,\s*#(?P<z>\d+)\s*,\s*#(?P<x>\d+)\s*\)\s*;", re.I)
dir_re = re.compile(r"#(?P<id>\d+)\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<d>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)

dir_map={}
for m in dir_re.finditer(s):
    did=int(m.group("id"))
    vec=[float(x) for x in m.group("d").split(",")]
    while len(vec)<3: vec.append(0.0)
    dir_map[did]=tuple(vec[:3])
axis_map={}
for m in axis_re.finditer(s):
    axis_map[int(m.group("id"))]={"p":int(m.group("p")),"z":int(m.group("z")),"x":int(m.group("x"))}
plane_map={}
for m in plane_re.finditer(s):
    plane_map[int(m.group("id"))]={"axis":axis_map.get(int(m.group("ax")))}

def point_plane_dist(p, origin, normal):
    nx,ny,nz=normal
    nn=(nx*nx+ny*ny+nz*nz)**0.5 or 1.0
    nx/=nn; ny/=nn; nz/=nn
    ox,oy,oz=origin
    return abs((p[0]-ox)*nx + (p[1]-oy)*ny + (p[2]-oz)*nz)

# Walk loops to detect continuity problems and build edge usage
from collections import Counter, defaultdict
edge_usage = Counter()
loop_problems=[]
repeat_vertices_in_loop=[]
face_vertices=defaultdict(list)

for fid,f in faces.items():
    for bid in f["bounds"]:
        lb = face_outer_bound.get(bid)
        if not lb: continue
        lid = lb["loop"]
        oids = edge_loops.get(lid, [])
        prev_tail=None
        loop_vertex_ids=[]
        for oid in oids:
            oe = oriented_edges.get(oid)
            if not oe:
                loop_problems.append({"face":fid,"loop":lid,"issue":"oriented_edge_missing","oriented_edge":oid})
                continue
            eid = oe["edge"]; e = edges.get(eid)
            if not e:
                loop_problems.append({"face":fid,"loop":lid,"issue":"edge_missing","edge":eid})
                continue
            forward = oe["sense"]
            start = e["v1"] if forward else e["v2"]
            end   = e["v2"] if forward else e["v1"]
            if prev_tail is not None and start != prev_tail:
                loop_problems.append({"face":fid,"loop":lid,"issue":"loop_gap_or_order","expected":prev_tail,"got":start,"oriented_edge":oid,"edge":eid})
            prev_tail=end
            loop_vertex_ids.append(start)
            face_vertices[fid].append(start)
            # undirected usage
            k = tuple(sorted((e["v1"], e["v2"])))
            edge_usage[k]+=1
        if prev_tail is not None:
            loop_vertex_ids.append(prev_tail)
            if loop_vertex_ids[0] != loop_vertex_ids[-1]:
                loop_problems.append({"face":fid,"loop":lid,"issue":"loop_not_closed","start":loop_vertex_ids[0],"end":loop_vertex_ids[-1]})
        counts = Counter(loop_vertex_ids)
        repeats = [v for v,c in counts.items() if c>2]
        if repeats:
            repeat_vertices_in_loop.append({"face":fid,"loop":lid,"vertex_ids":repeats,"counts":[counts[v] for v in repeats]})

# Classify edge usage
boundary_edges=[]; nonmanifold=[]
for (v1,v2),c in edge_usage.items():
    if c==1: boundary_edges.append({"v1":v1,"v2":v2,"usage":c})
    elif c>2: nonmanifold.append({"v1":v1,"v2":v2,"usage":c})

# Small edges
tiny_mm=1e-3; short_mm=0.05
tiny_edges=[]; short_edges=[]
for eid,e in edges.items():
    if e["length"] is None: continue
    Lmm=e["length"]*unit_scale_mm
    if Lmm<=tiny_mm: tiny_edges.append({"edge_id":eid,"v1":e["v1"],"v2":e["v2"],"length_mm":Lmm})
    elif Lmm<=short_mm: short_edges.append({"edge_id":eid,"v1":e["v1"],"v2":e["v2"],"length_mm":Lmm})

# Duplicate vertices (coincident)
tol_mm=1e-4; tol_units=tol_mm/unit_scale_mm if unit_scale_mm else tol_mm
bins=defaultdict(list)
for vid,p in vertex_to_point.items():
    key=(round(p[0]/tol_units), round(p[1]/tol_units), round(p[2]/tol_units))
    bins[key].append((vid,p))
coincident_groups=[items for items in bins.values() if len(items)>1]

# BBox
coords=list(vertex_to_point.values())
bbox=None
if coords:
    xs=[c[0] for c in coords]; ys=[c[1] for c in coords]; zs=[c[2] for c in coords]
    bbox={"xmin":min(xs),"xmax":max(xs),"ymin":min(ys),"ymax":max(ys),"zmin":min(zs),"zmax":max(zs),
          "dx":max(xs)-min(xs),"dy":max(ys)-min(ys),"dz":max(zs)-min(zs)}

# Planarity for PLANE faces
plane_face_deviations=[]
# Build direction & origin from plane axis
for fid,f in faces.items():
    sid = f["surface"]
    # find if sid is PLANE
    if re.search(rf"#\s*{sid}\s*=\s*PLANE", s):
        # find axis id
        m = re.search(rf"#\s*{sid}\s*=\s*PLANE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*\)\s*;", s, re.I)
        if not m: continue
        axid = int(m.group(1))
        m2 = re.search(rf"#\s*{axid}\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*#(\d+)\s*,\s*#(\d+)\s*\)\s*;", s, re.I)
        if not m2: continue
        ppid=int(m2.group(1)); zdid=int(m2.group(2))
        origin = points.get(ppid); normal = None
        m3 = re.search(rf"#\s*{zdid}\s*=\s*DIRECTION\s*\(\s*'[^']*'\s*,\s*\(\s*([-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", s, re.I)
        if m3:
            vec=[float(x) for x in m3.group(1).split(",")]
            while len(vec)<3: vec.append(0.0)
            normal=tuple(vec[:3])
        if origin and normal:
            verts=[vertex_to_point.get(vid) for vid in set(face_vertices[fid]) if vid in vertex_to_point]
            if verts:
                dists=[point_plane_dist(p, origin, normal) for p in verts]
                maxd=max(dists)
                plane_face_deviations.append({"face":fid,"surface":sid,"max_abs_distance_units":maxd,"max_abs_distance_mm":maxd*unit_scale_mm,"num_vertices":len(verts)})

# DataFrames
df_entities = pd.DataFrame(sorted(entity_counts.items()), columns=["Entity","Count"])
df_boundary = pd.DataFrame(boundary_edges)
df_nonmanifold = pd.DataFrame(nonmanifold)
df_loop_issues = pd.DataFrame(loop_problems)
df_repeat_vtx = pd.DataFrame(repeat_vertices_in_loop)
df_tiny = pd.DataFrame(tiny_edges)
df_short = pd.DataFrame(short_edges)
df_planes = pd.DataFrame(plane_face_deviations).sort_values("max_abs_distance_mm", ascending=False) if plane_face_deviations else pd.DataFrame()

'''
display_dataframe_to_user("Entity Counts (o.step)", df_entities)
if not df_boundary.empty: display_dataframe_to_user("Boundary Edges (used by exactly 1 face loop)", df_boundary)
if not df_nonmanifold.empty: display_dataframe_to_user("Non-manifold Edges (used by >2 face loops)", df_nonmanifold)
if not df_loop_issues.empty: display_dataframe_to_user("Loop Continuity Issues", df_loop_issues)
if not df_repeat_vtx.empty: display_dataframe_to_user("Loops with Repeated Vertices (likely self-touch)", df_repeat_vtx)
if not df_tiny.empty: display_dataframe_to_user("Degenerate Edges (≈0 length)", df_tiny)
if not df_short.empty: display_dataframe_to_user("Suspiciously Short Edges", df_short)
if not df_planes.empty: display_dataframe_to_user("Planar Face Deviations", df_planes)
'''

summary = {
    "units": units, "bbox": bbox, "counts": dict(entity_counts),
    "num_vertices": len(vertex_to_point), "num_edges": len(edges), "num_faces": len(faces),
    "num_boundary_edges": len(boundary_edges), "num_nonmanifold_edges": len(nonmanifold),
    "num_loop_issues": len(loop_problems), "num_loops_with_repeats": len(df_repeat_vtx),
    "num_tiny_edges": len(tiny_edges), "num_short_edges": len(short_edges),
    "num_coincident_vertex_groups_est": None,  # skipped to save time
    "planar_deviation_max_mm": max((r["max_abs_distance_mm"] for r in plane_face_deviations), default=0.0),
}
report_path = "o_step_diagnostics.json"
with open(report_path,"w") as f:
    json.dump(summary, f, indent=2)

summary, f"Saved report to {report_path}"


# Extend face parsing to include FACE_SURFACE in addition to ADVANCED_FACE.
import re, json
from collections import defaultdict, Counter
import pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Reuse previously computed maps lightly by re-parsing essentials
# Bounds and loops
fob_re = re.compile(r"#(?P<id>\d+)\s*=\s*FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*#(?P<loop>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
face_outer_bound={}
for m in fob_re.finditer(s):
    face_outer_bound[int(m.group("id"))]={"loop":int(m.group("loop")),"sense":m.group("sense").upper()=="T"}

loop_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
edge_loops={}
for m in loop_re.finditer(s):
    lid=int(m.group("id"))
    items=[int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]
    edge_loops[lid]=items

# Oriented edges, edges, vertices, points (minimal for loop continuity)
pt_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<xyz>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)
points={}
for m in pt_re.finditer(s):
    pid=int(m.group("id")); xyz=[float(x) for x in m.group("xyz").split(",")]
    while len(xyz)<3: xyz.append(0.0)
    points[pid]=tuple(xyz[:3])
vtx_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.I)
vertex_to_point={}
for m in vtx_re.finditer(s):
    vid=int(m.group("id")); pid=int(m.group("pid"))
    if pid in points: vertex_to_point[vid]=points[pid]

edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges={}
for m in edge_re.finditer(s):
    eid=int(m.group("id")); v1=int(m.group("v1")); v2=int(m.group("v2"))
    edges[eid]={"v1":v1,"v2":v2}

oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\$,\s*\$,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
oriented_edges={}
for m in oedge_re.finditer(s):
    oriented_edges[int(m.group("id"))]={"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"}

# Faces: ADVANCED_FACE or FACE_SURFACE
face_re = re.compile(r"#(?P<id>\d+)\s*=\s*(?P<type>ADVANCED_FACE|FACE_SURFACE)\s*\(\s*\((?P<bounds>[^)]*)\)\s*,\s*#(?P<surf>\d+)\s*(?:,\s*\.(?P<sense>T|F)\.\s*)?\)\s*;", re.I|re.S)
faces={}
for m in face_re.finditer(s):
    fid=int(m.group("id"))
    bounds=[int(i.strip().lstrip("#")) for i in m.group("bounds").replace("\n"," ").split(",") if i.strip().startswith("#")]
    surf=int(m.group("surf")); sense = (m.group("sense") or "T").upper()=="T"
    faces[fid]={"type":m.group("type").upper(),"bounds":bounds,"surface":surf,"sense":sense}

# Check that OPEN_SHELL lists these faces
open_shell_re = re.compile(r"#(?P<id>\d+)\s*=\s*OPEN_SHELL\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
open_shell_faces=[]
m = open_shell_re.search(s)
if m:
    open_shell_faces=[int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]

missing_faces=[fid for fid in open_shell_faces if fid not in faces]

df_faces = pd.DataFrame([{"face_id":fid,"type":f["type"],"num_bounds":len(f["bounds"]),"surface":f["surface"]} for fid,f in faces.items()])
df_missing = pd.DataFrame(missing_faces, columns=["face_id_referenced_by_open_shell_but_not_parsed"])

#display_dataframe_to_user("Faces parsed (ADVANCED_FACE or FACE_SURFACE)", df_faces)
#if not df_missing.empty:
#    display_dataframe_to_user("Faces referenced by OPEN_SHELL but not present as ADVANCED_FACE/FACE_SURFACE", df_missing)

summary={"num_faces_parsed":len(faces), "open_shell_faces_count":len(open_shell_faces), "missing_faces_in_parsed":len(missing_faces)}
report_path="o_step_faces_summary.json"
with open(report_path,"w") as f:
    json.dump(summary,f,indent=2)
summary, f"Saved face summary to {report_path}"

# Extract the OPEN_SHELL and show the exact entity IDs it references, plus a grep of those IDs in the file
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

open_shell_re = re.compile(r"#(?P<id>\d+)\s*=\s*OPEN_SHELL\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
m = open_shell_re.search(s)
open_shell_id = None
open_shell_faces = []
if m:
    open_shell_id = int(m.group("id"))
    open_shell_faces = [int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]

rows=[]
for fid in open_shell_faces:
    # search for an entity definition starting with #fid =
    pat = re.compile(rf"^#\s*{fid}\s*=\s*([A-Z0-9_]+)\s*\(", re.I|re.M)
    mm = pat.search(s)
    etype = mm.group(1).upper() if mm else None
    rows.append({"open_shell_id": open_shell_id, "referenced_face_id": fid, "entity_type_found": etype})

df = pd.DataFrame(rows)
#display_dataframe_to_user("OPEN_SHELL references and entity types", df)


# Show the raw text snippets for the ADVANCED_FACE entities referenced by OPEN_SHELL to understand why the previous parser missed them.
import re, textwrap, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

def snippet_for_id(n, context=2):
    # find the line index where "# n =" occurs
    lines = s.splitlines()
    idx = None
    for i,line in enumerate(lines):
        if re.match(rf"\s*#\s*{n}\s*=", line):
            idx = i; break
    if idx is None: return ""
    start=max(0, idx-context); end=min(len(lines), idx+10)  # show a few following lines
    return "\n".join(lines[start:end])

open_shell_faces = [195,215,235,255]
snips=[{"id":fid, "snippet": snippet_for_id(fid)} for fid in open_shell_faces]
df = pd.DataFrame(snips)
#display_dataframe_to_user("ADVANCED_FACE raw snippets", df)

# Expand the snippet capture to include more following lines to reveal the ADVANCED_FACE definitions.
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

def snippet_block_for_id(n, after=20):
    lines = s.splitlines()
    idx = None
    for i,line in enumerate(lines):
        if re.match(rf"\s*#\s*{n}\s*=", line):
            idx = i; break
    if idx is None: return ""
    start=max(0, idx-1); end=min(len(lines), idx+after)
    return "\n".join(lines[start:end])

open_shell_faces = [195,215,235,255]
rows=[]
for fid in open_shell_faces:
    # scroll ahead to find the actual ADVANCED_FACE line near this area
    snippet = snippet_block_for_id(fid, after=10)
    rows.append({"id":fid, "snippet": snippet})

#display_dataframe_to_user("Entity blocks near referenced face IDs", pd.DataFrame(rows))

# Print the exact single line that defines each referenced entity number.
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

def entity_line(n):
    m = re.search(rf"^#\s*{n}\s*=\s*([A-Z0-9_]+)\s*\(.*", s, re.I|re.M)
    if m:
        etype=m.group(1).upper()
        # capture full balanced parentheses line if it ends with ';'
        # simpler: get the current line
        line = re.search(rf"^#\s*{n}\s*=.*;$", s, re.I|re.M)
        return etype, (line.group(0) if line else "multiline or not on one line")
    return None, ""

rows=[]
for fid in [195,215,235,255]:
    etype, line = entity_line(fid)
    rows.append({"id":fid, "entity_type":etype, "line":line[:200]})
#display_dataframe_to_user("Exact entity type for referenced IDs", pd.DataFrame(rows))

# Print the exact single line that defines each referenced entity number.
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

def entity_line(n):
    m = re.search(rf"^#\s*{n}\s*=\s*([A-Z0-9_]+)\s*\(.*", s, re.I|re.M)
    if m:
        etype=m.group(1).upper()
        # capture full balanced parentheses line if it ends with ';'
        # simpler: get the current line
        line = re.search(rf"^#\s*{n}\s*=.*;$", s, re.I|re.M)
        return etype, (line.group(0) if line else "multiline or not on one line")
    return None, ""

rows=[]
for fid in [195,215,235,255]:
    etype, line = entity_line(fid)
    rows.append({"id":fid, "entity_type":etype, "line":line[:200]})
#display_dataframe_to_user("Exact entity type for referenced IDs", pd.DataFrame(rows))

# Robust re-parse faces using a more permissive regex and recompute loop continuity and edge usage.
import re, math, json
from collections import defaultdict, Counter
import pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Re-parse basics
pt_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<xyz>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)
points={}
for m in pt_re.finditer(s):
    pid=int(m.group("id")); xyz=[float(x) for x in m.group("xyz").split(",")]
    while len(xyz)<3: xyz.append(0.0)
    points[pid]=tuple(xyz[:3])

vtx_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.I)
vertex_to_point={}
for m in vtx_re.finditer(s):
    vid=int(m.group("id")); pid=int(m.group("pid"))
    if pid in points: vertex_to_point[vid]=points[pid]

edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges={}
for m in edge_re.finditer(s):
    eid=int(m.group("id")); v1=int(m.group("v1")); v2=int(m.group("v2"))
    p1=vertex_to_point.get(v1); p2=vertex_to_point.get(v2)
    edges[eid]={"v1":v1,"v2":v2,"p1":p1,"p2":p2}

oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\$,\s*\$,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
oriented_edges={}
for m in oedge_re.finditer(s):
    oriented_edges[int(m.group("id"))]={"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"}

loop_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
edge_loops={}
for m in loop_re.finditer(s):
    lid=int(m.group("id"))
    items=[int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]
    edge_loops[lid]=items

fob_re = re.compile(r"#(?P<id>\d+)\s*=\s*FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*#(?P<loop>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
face_outer_bound={}
for m in fob_re.finditer(s):
    face_outer_bound[int(m.group("id"))]={"loop":int(m.group("loop")),"sense":m.group("sense").upper()=="T"}

# New face regex: capture label, bounds tuple, surface ref, optional sense
face_re = re.compile(r"#(?P<id>\d+)\s*=\s*(ADVANCED_FACE|FACE_SURFACE)\s*\(\s*'[^']*'\s*,\s*\((?P<bounds>[^)]*)\)\s*,\s*#(?P<surf>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I|re.S)
faces={}
for m in face_re.finditer(s):
    fid=int(m.group("id"))
    bounds=[int(i.strip().lstrip("#")) for i in m.group("bounds").replace("\n"," ").split(",") if i.strip().startswith("#")]
    faces[fid]={"bounds":bounds,"surface":int(m.group("surf")),"sense":m.group("sense").upper()=="T"}

# Verify faces referenced by OPEN_SHELL exist
open_shell_re = re.compile(r"#(?P<id>\d+)\s*=\s*OPEN_SHELL\s*\(\s*'[^']*'\s*,\s*\((?P<items>[^)]*)\)\s*\)\s*;", re.I|re.S)
open_shell_faces=[]
m = open_shell_re.search(s)
if m:
    open_shell_faces=[int(i.strip().lstrip("#")) for i in m.group("items").replace("\n"," ").split(",") if i.strip().startswith("#")]

missing=[fid for fid in open_shell_faces if fid not in faces]

# Loop continuity and edge usage
edge_usage=Counter()
loop_issues=[]
for fid in open_shell_faces:
    fbounds = faces.get(fid, {}).get("bounds", [])
    for bid in fbounds:
        lid = face_outer_bound.get(bid,{}).get("loop")
        if not lid: 
            loop_issues.append({"face":fid,"issue":"missing_FACE_OUTER_BOUND", "bound_id":bid})
            continue
        oids = edge_loops.get(lid, [])
        prev_tail=None
        first_head=None
        for i,oid in enumerate(oids):
            oe = oriented_edges.get(oid)
            if not oe:
                loop_issues.append({"face":fid,"loop":lid,"issue":"oriented_edge_missing","oriented_edge":oid})
                continue
            eid = oe["edge"]; e = edges.get(eid)
            if not e:
                loop_issues.append({"face":fid,"loop":lid,"issue":"edge_missing","edge":eid})
                continue
            start = e["v1"] if oe["sense"] else e["v2"]
            end   = e["v2"] if oe["sense"] else e["v1"]
            if i==0: first_head=start
            if prev_tail is not None and start != prev_tail:
                loop_issues.append({"face":fid,"loop":lid,"issue":"loop_gap_or_order","expected":prev_tail,"got":start,"edge":eid,"oriented_edge":oid})
            prev_tail=end
            k = tuple(sorted((e["v1"], e["v2"])))
            edge_usage[k]+=1
        if prev_tail is not None and first_head is not None and prev_tail != first_head:
            loop_issues.append({"face":fid,"loop":lid,"issue":"loop_not_closed","start":first_head,"end":prev_tail})

df_faces = pd.DataFrame([{"face_id":fid, "num_bounds":len(faces[fid]["bounds"])} for fid in open_shell_faces if fid in faces])
df_missing = pd.DataFrame(missing, columns=["open_shell_face_missing"])
df_loop = pd.DataFrame(loop_issues)
df_usage = pd.DataFrame([{"v1":v1,"v2":v2,"usage":c} for (v1,v2),c in edge_usage.items()])

#display_dataframe_to_user("Faces referenced by OPEN_SHELL (parsed)", df_faces)
#if not df_missing.empty: display_dataframe_to_user("OPEN_SHELL faces missing in parsed set", df_missing)
#if not df_loop.empty: display_dataframe_to_user("Loop continuity issues (per face)", df_loop)
#display_dataframe_to_user("Undirected edge usage across faces", df_usage)

# Manually inspect the four faces we saw earlier (195, 215, 235, 255) and their bounds/loops content.
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

face_ids = [195,215,235,255]

# For each face id, find its FACE_OUTER_BOUND id immediately preceding it (common pattern)
data=[]
for fid in face_ids:
    # FACE_OUTER_BOUND likely has id fid-1
    m = re.search(rf"#\s*{fid-1}\s*=\s*FACE_OUTER_BOUND\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*\.(T|F)\.\s*\)\s*;", s, re.I)
    loop_id = int(m.group(1)) if m else None
    # Extract the EDGE_LOOP content
    items=[]
    if loop_id is not None:
        m2 = re.search(rf"#\s*{loop_id}\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)\s*;", s, re.I|re.S)
        if m2:
            items = [int(i.strip().lstrip("#")) for i in m2.group(1).replace("\n"," ").split(",") if i.strip().startswith("#")]
    data.append({"face_id":fid, "face_outer_bound_id": (fid-1 if m else None), "edge_loop_id": loop_id, "num_items_in_loop": len(items), "loop_items_sample": items[:10]})
df = pd.DataFrame(data)
#display_dataframe_to_user("Faces -> bounds -> loops (manual probe)", df)

# Also show the sequence of oriented edges for each loop in a separate table
rows=[]
for rec in data:
    lid=rec["edge_loop_id"]; fid=rec["face_id"]
    if not lid: continue
    m2 = re.search(rf"#\s*{lid}\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)\s*;", s, re.I|re.S)
    if not m2: continue
    items = [i.strip() for i in m2.group(1).replace("\n"," ").split(",") if i.strip().startswith("#")]
    rows.extend([{"face_id":fid,"loop_id":lid,"order":k,"oriented_edge_ref":it} for k,it in enumerate(items)])
#display_dataframe_to_user("Loop oriented edges (sequence)", pd.DataFrame(rows))

# Resolve oriented edge -> underlying edge -> vertices, to see if the loop is degenerate (same segment repeated).
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Parse oriented edges and edges
oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*\$,\s*\$,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
oriented_edges={}
for m in oedge_re.finditer(s):
    oriented_edges[int(m.group("id"))]={"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"}

vtx_re = re.compile(r"#(?P<id>\d+)\s*=\s*VERTEX_POINT\s*\(\s*'[^']*'\s*,\s*#(?P<pid>\d+)\s*\)\s*;", re.I)
pt_re = re.compile(r"#(?P<id>\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*(?P<xyz>[-+0-9Ee\.\s,]+)\s*\)\s*\)\s*;", re.I)
points={}
for m in pt_re.finditer(s):
    pid=int(m.group("id")); xyz=[float(x) for x in m.group("xyz").split(",")]
    while len(xyz)<3: xyz.append(0.0)
    points[pid]=tuple(xyz[:3])
vertex_to_point={}
for m in vtx_re.finditer(s):
    vid=int(m.group("id")); pid=int(m.group("pid"))
    if pid in points: vertex_to_point[vid]=points[pid]

edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges={}
for m in edge_re.finditer(s):
    eid=int(m.group("id")); v1=int(m.group("v1")); v2=int(m.group("v2"))
    edges[eid]={"v1":v1,"v2":v2}

# Get loops again
loop_ids=[193,213,233,253]
rows=[]
for lid in loop_ids:
    m2 = re.search(rf"#\s*{lid}\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)\s*;", s, re.I|re.S)
    if not m2: continue
    items=[int(i.strip().lstrip("#")) for i in m2.group(1).replace("\n"," ").split(",") if i.strip().startswith("#")]
    for k,oid in enumerate(items):
        oe = oriented_edges.get(oid,{})
        eid = oe.get("edge"); sense = oe.get("sense")
        e = edges.get(eid,{})
        rows.append({"loop_id":lid,"order":k,"oriented_edge_id":oid,"edge_id":eid,"edge_v1":e.get("v1"),"edge_v2":e.get("v2"),"oe_sense":sense})
df = pd.DataFrame(rows)
#display_dataframe_to_user("Resolved loop contents", df)

# Re-parse ORIENTED_EDGE with a general pattern that doesn't assume '$' placeholders.
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

oedge_re_general = re.compile(
    r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*[^,]*\s*,\s*[^,]*\s*,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;",
    re.I)
oriented_edges={}
for m in oedge_re_general.finditer(s):
    oriented_edges[int(m.group("id"))]={"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"}

edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edges={}
for m in edge_re.finditer(s):
    edges[int(m.group("id"))]={"v1":int(m.group("v1")),"v2":int(m.group("v2"))}

# Show mapped data for the specific loop ids we saw
loop_ids=[193,213,233,253]
rows=[]
for lid in loop_ids:
    m2 = re.search(rf"#\s*{lid}\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)\s*;", s, re.I|re.S)
    if not m2: continue
    items=[int(i.strip().lstrip("#")) for i in m2.group(1).replace("\n"," ").split(",") if i.strip().startswith("#")]
    for k,oid in enumerate(items):
        oe = oriented_edges.get(oid,{})
        eid = oe.get("edge"); sense = oe.get("sense")
        e = edges.get(eid,{})
        rows.append({"loop_id":lid,"order":k,"oriented_edge_id":oid,"edge_id":eid,"edge_v1":e.get("v1"),"edge_v2":e.get("v2"),"oe_sense":sense})
df = pd.DataFrame(rows)
#display_dataframe_to_user("Resolved loop contents (general OE parser)", df)

# Check continuity for the four loops explicitly, using the generalized OE parser
import re, pandas as pd


PATH = "o.step"
with open(PATH, "r", errors="ignore") as f:
    s = f.read()

# Parse oriented edges & edges
oedge_re = re.compile(r"#(?P<id>\d+)\s*=\s*ORIENTED_EDGE\s*\(\s*'[^']*'\s*,\s*[^,]*\s*,\s*[^,]*\s*,\s*#(?P<edge>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)
edge_re = re.compile(r"#(?P<id>\d+)\s*=\s*EDGE_CURVE\s*\(\s*'[^']*'\s*,\s*#(?P<v1>\d+)\s*,\s*#(?P<v2>\d+)\s*,\s*#(?P<curve>\d+)\s*,\s*\.(?P<sense>T|F)\.\s*\)\s*;", re.I)

oriented_edges={int(m.group("id")):{"edge":int(m.group("edge")),"sense":m.group("sense").upper()=="T"} for m in oedge_re.finditer(s)}
edges={int(m.group("id")):{"v1":int(m.group("v1")),"v2":int(m.group("v2"))} for m in edge_re.finditer(s)}

def loop_items(lid):
    m2 = re.search(rf"#\s*{lid}\s*=\s*EDGE_LOOP\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)\s*\)\s*;", s, re.I|re.S)
    if not m2: return []
    return [int(i.strip().lstrip("#")) for i in m2.group(1).replace("\n"," ").split(",") if i.strip().startswith("#")]

results=[]
for lid in [193,213,233,253]:
    items = loop_items(lid)
    prev_tail=None; first_head=None
    for k,oid in enumerate(items):
        oe=oriented_edges.get(oid,{})
        eid=oe.get("edge"); sense=oe.get("sense")
        e=edges.get(eid,{})
        start = e.get("v1") if sense else e.get("v2")
        end   = e.get("v2") if sense else e.get("v1")
        if k==0: first_head=start
        ok = (prev_tail is None) or (start==prev_tail)
        results.append({"loop_id":lid,"order":k,"oriented_edge_id":oid,"edge_id":eid,"start_vertex":start,"end_vertex":end,"continuity_ok":ok})
        prev_tail=end
    if first_head is not None and prev_tail is not None:
        results.append({"loop_id":lid,"order":"closure","oriented_edge_id":None,"edge_id":None,"start_vertex":first_head,"end_vertex":prev_tail,"continuity_ok": first_head==prev_tail})

df = pd.DataFrame(results)
#display_dataframe_to_user("Loop continuity check (four loops)", df)



