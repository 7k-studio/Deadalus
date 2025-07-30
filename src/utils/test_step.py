import numpy as np

# Input arrays (from user)
ps = np.array([
    [0.04000872, 0.16, 0.59000437, 0.99000437],
    [-0.02498604, -0.04826651, 0.01560438, -0.00500872]
])
ss = np.array([
    [0.03999127, 0.2, 0.88999564, 0.98999564],
    [0.02501396, 0.08972666, 0.03169268, 0.00499127]
])
le = np.array([
    [4.00087242e-02, 6.01258502e-06, -3.08537587e-06, 3.99912709e-02],
    [-2.49860358e-02, -1.72247866e-02, 8.83895043e-03, 2.50139611e-02]
])
te = np.array([
    [0.99000437, 1.00000482, 0.99999797, 0.98999564],
    [-0.00500872, -0.00552408, 0.00232051, 0.00499127]
])

# Classes from user, lightly modified with .export() method for each
class CartesianPoint:
    def __init__(self, idx, X, Y, Z):
        self.idx = idx
        self.name = 'CARTESIAN_POINT'
        self.var = 'NONE'
        self.X = X
        self.Y = Y
        self.Z = Z

    def export(self):
        return f"#{self.idx} = {self.name} ( '{self.var}', ( {round(self.X, 10)}, {round(self.Y, 10)}, {round(self.Z, 10)} ) ) ;"

class VertexPoint:
    def __init__(self, idx, cp_index):
        self.idx = idx
        self.name = 'VERTEX_POINT'
        self.var = 'NONE'
        self.cartesian_point_idx = cp_index

    def export(self):
        return f"#{self.idx} = {self.name} ( '{self.var}', #{self.cartesian_point_idx} ) ;"

class BsplineWithKnots:
    def __init__(self, idx, points_indexes):
        self.idx = idx
        self.name = 'B_SPLINE_CURVE_WITH_KNOTS'
        self.variable = 'NONE'
        self.number = 3
        self.points_indexes = points_indexes
        self.spec1 = '.UNSPECIFIED.'
        self.spec2 = '.T.'
        self.spec3 = '.T.'
        self.spec4 = [4, 4]
        self.spec5 = [0.0, 1.0]

    def export(self):
        pts = ', '.join(f'#{i}' for i in self.points_indexes)
        return f"#{self.idx} = {self.name} ( '{self.variable}', {self.number}, ( {pts} ), {self.spec1}, {self.spec2}, {self.spec3}, ( {self.spec4[0]}, {self.spec4[1]} ), ( {self.spec5[0]:.18f}, {self.spec5[1]:.18f} ) ) ;"

class EdgeCurve:
    def __init__(self, idx, VP1_idx, VP2_idx, Curv_idx):
        self.idx = idx
        self.name = 'EDGE_CURVE'
        self.vertex_point_1_idx = VP1_idx
        self.vertex_point_2_idx = VP2_idx
        self.curve_idx = Curv_idx
        self.spec = '.T.'

    def export(self):
        return f"#{self.idx} = {self.name} ( #{self.vertex_point_1_idx}, #{self.vertex_point_2_idx}, #{self.curve_idx}, {self.spec} ) ;"

# Helper
def normalized_coords(x, y, z):
    return (
        float(round(x, 10)),
        float(round(y, 10)),
        float(round(z, 10))
    )

# Build STEP objects
current_idx = 1
point_index_map = {}
cp_store = []
entities = []

def add_curve(points_2d):
    global current_idx
    cp_indices = []
    ve_indices = []
    for i in range(points_2d.shape[1]):
        coords = normalized_coords(points_2d[0, i], points_2d[1, i], 0.0)
        if coords not in point_index_map:
            cp = CartesianPoint(current_idx, *coords)
            cp_store.append(cp)
            point_index_map[coords] = current_idx
            current_idx += 1
        cp_idx = point_index_map[coords]
        cp_indices.append(cp_idx)

        if i == 0 or i == points_2d.shape[1] - 1:
            ve = VertexPoint(current_idx, cp_idx)
            entities.append(ve)
            ve_indices.append(current_idx)
            current_idx += 1

    bspline = BsplineWithKnots(current_idx, cp_indices)
    entities.append(bspline)
    bspline_idx = current_idx
    current_idx += 1

    ec = EdgeCurve(current_idx, ve_indices[0], ve_indices[1], bspline_idx)
    entities.append(ec)
    current_idx += 1

# Add all curves
for curve in [ps, ss, le, te]:
    add_curve(curve)

# Collect all exports
step_lines = [cp.export() for cp in cp_store] + [e.export() for e in entities]
step_content = "\n".join(step_lines)
step_content[:1000]  # Preview
