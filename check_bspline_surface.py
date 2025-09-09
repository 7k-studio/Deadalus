# Save as check_bspline_surface.py and run with python
# Needs geomdl (pip install geomdl)

from geomdl import BSpline
from geomdl.visualization import VisMPL
import numpy as np

# --- USER: paste the surface parameters here ---
# Example values (replace with your actual data from the STEP entry):
degree_u = 3
degree_v = 3

# poles flattened as given in STEP, in the same order you wrote them.
# For LE example, replace the array below with the 16 control point tuples
poles = [
   ( 0.9900043671, -0.0050087247, 0.0 ),
   ( 1.0000048207, -0.0055240757, 0.0 ),
   ( 0.999997975, 0.0023205072, 0.0 ),
   ( 0.9899956405, 0.0049912715, 0.0 ),
   ( 0.9900043671, -0.0050087247, 0.1 ),
   ( 1.0000048207, -0.0055240757, 0.1 ),
   ( 0.999997975, 0.0023205072, 0.1 ),
   ( 0.9899956405, 0.0049912715, 0.1 ),
   ( 0.9900043671, 0.0949912753, 0.2 ),
   ( 1.0000048207, 0.0944759243, 0.2 ),
   ( 0.999997975, 0.1023205072, 0.2 ),
   ( 0.9899956405, 0.1049912715, 0.2 ),
   ( 0.9900043671, 0.0949912753, 0.3 ),
   ( 1.0000048207, 0.0944759243, 0.3 ),
   ( 0.999997975, 0.1023205072, 0.3 ),
   ( 0.9899956405, 0.1049912715, 0.3 ),
  # ... fill the remaining 12 points in the exact order from your STEP ...
]

# knot vectors (replace with the ones in your STEP)
knot_u = [0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0]  # example clamped cubic with 4 poles
knot_v = [0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0]

# reshape to 2D if needed:
n_u = 4
n_v = 4
if len(poles) != n_u*n_v:
    raise SystemExit("Pole count mismatch: expected {} got {}".format(n_u*n_v,len(poles)))

# Create BSpline surface
surf = BSpline.Surface()
surf.degree_u = degree_u
surf.degree_v = degree_v
surf.set_ctrlpts(poles, n_u, n_v)  # NOTE: this expects row-major: u rows of v columns
surf.knotvector_u = knot_u
surf.knotvector_v = knot_v

# Evaluate surface at a small grid and compare to poles at isoparametric positions
uvs = [(i/(n_u-1), j/(n_v-1)) for i in range(n_u) for j in range(n_v)]  # param corners/mids
eval_pts = [surf.evaluate_single(u, v) for (u, v) in uvs]

# Compare eval_pts to control points if you expect them to match at corners/edges
print("Comparison of evaluated surface points at grid vs control points (STEP order):")
for idx, (cp, ev) in enumerate(zip(poles, eval_pts)):
    dx = ev[0] - cp[0]
    dy = ev[1] - cp[1]
    dz = ev[2] - cp[2]
    print(f"idx {idx}: CP={cp}  eval={tuple(ev)}  delta=({dx:.6e},{dy:.6e},{dz:.6e})")

# Additional helpful prints:
print("knot_u:", knot_u)
print("knot_v:", knot_v)