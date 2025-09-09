grid = [
    [[0.0399912709169779, 0.0250139611106448, 0.0], [0.0399912709169779, 0.02501396111064479, 0.1], [0.0399912709169779, 0.0250139611106448, 0.2], [0.0399912709169779, 0.0250139611106448, 0.3]],
    [[0.2000000000000000, 0.0897266641547486, 0.0], [0.2000000000000000, 0.08972666415474867, 0.1], [0.2000000000000000, 0.0897266641547486, 0.2], [0.2000000000000000, 0.0897266641547486, 0.3]],
    [[0.8899956404851413, 0.0316926806230836, 0.0], [0.8899956404851415, 0.03169268062308364, 0.1], [0.8899956404851412, 0.0316926806230836, 0.2], [0.8899956404851413, 0.0316926806230836, 0.3]],
    [[0.9899956404851413, 0.0049912714509900, 0.0], [0.9899956404851413, 0.00499127145099009, 0.1], [0.9899956404851413, 0.0049912714509900, 0.2], [0.9899956404851413, 0.0049912714509900, 0.3]]
]

rows = len(grid)
cols = len(grid[0])

cp_store = []
ve_store = []

tmp_object_grid = [[0 for col in range(cols)] for row in range(rows)]
print(tmp_object_grid)

for i in range(cols):
    for j in range(rows):
        print(grid[j][i])


txt = 'le'
print(len(txt))

txt = [f'segment {i} te', f'segment {i+1} te', f'segment {i} te_ps', f'segment {i} te_ss']

for obj in txt:
    print(len(obj))

max_u_raport = max(len(txt[0]), len(txt[1]))
max_v_raport = max(len(txt[2]), len(txt[3]))

report_grid = [["" for col in range(max_u_raport)] for row in range(max_v_raport)]
print(report_grid)

for i in range(max_u_raport):
    for j in range(max_v_raport):
        if i > 2:
            report_grid = txt[0]

print(report_grid)

txt = [
    f'segment {i} te',      # top
    f'segment {i+1} te',    # bottom
    f'segment {i} te_ps',   # left
    f'segment {i} te_ss'    # right
]

# strip out "segment " part
txt = [t.replace("segment ", "") for t in txt]

# expand horizontal edges with spaces
top = " ".join(txt[0])
bottom = " ".join(txt[1])
left, right = txt[2], txt[3]

max_u = max(len(top), len(bottom)) + 4   # +4 for corner padding
max_v = max(len(left), len(right)) + 4

# make grid filled with spaces
report_grid = [[" " for _ in range(max_u)] for _ in range(max_v)]

# place top (centered)
start_top = (max_u - len(top)) // 2
report_grid[0][start_top:start_top+len(top)] = list(top)

# place bottom (centered)
start_bottom = (max_u - len(bottom)) // 2
report_grid[-1][start_bottom:start_bottom+len(bottom)] = list(bottom)

# place left (vertical, centered)
start_left = (max_v - len(left)) // 2
for j, ch in enumerate(left):
    report_grid[start_left+j][0] = ch

# place right (vertical, centered)
start_right = (max_v - len(right)) // 2
for j, ch in enumerate(right):
    report_grid[start_right+j][-1] = ch


print("_"*max_u)
# print as text
for row in report_grid:
    print("".join(row))

'''
    for i in range(len(segment.control_points[key][0, :])):
        coords = normalized_coords(
            segment.control_points[key][0, i],
            segment.control_points[key][1, i],
            segment.control_points[key][2, i],
        )
        cp = CartesianPoint(current_idx, desc='Control Point', X=coords[0], Y=coords[1], Z=coords[2])
        cp_store.append(cp)
        current_idx += 1
        print(current_idx)
        
    print("CP store:", cp_store)

    # Create Vertex Point of first point 
    ve = VertexPoint(current_idx, f"End point {key}", cp_store[0].idx)
    ve_store.append(ve)
    current_idx += 1

    # Create Vertex Point of last point 
    ve = VertexPoint(current_idx, f"End point {key}", cp_store[-1].idx)
    ve_store.append(ve)
    current_idx += 1

    print(current_idx)

    return current_idx, cp_store, ve_store

print(grid)'''