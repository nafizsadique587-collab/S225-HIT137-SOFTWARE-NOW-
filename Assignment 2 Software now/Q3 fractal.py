
import os
import sys
import math
import argparse

# Optional plotting
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None  # Plotting will be skipped gracefully

def regular_polygon(n_sides: int, side_len: float):
    """Return list of (x,y) vertices (closed, last=first) for a regular n-gon with given side length."""
    if n_sides < 3:
        raise ValueError("Number of sides must be >= 3")
    # Circumradius R from side length s: s = 2 R sin(pi/n)
    R = side_len / (2 * math.sin(math.pi / n_sides))
    pts = []
    for k in range(n_sides):
        theta = 2 * math.pi * k / n_sides
        x = R * math.cos(theta)
        y = R * math.sin(theta)
        pts.append((x, y))
    pts.append(pts[0])  # close the polygon
    return pts

def koch_subdivide(p0, p1):
    """Given segment p0->p1, return 5 points subdividing into 4 Koch segments: p0, a, peak, b, p1."""
    (x0,y0),(x1,y1) = p0,p1
    dx, dy = x1-x0, y1-y0
    a = (x0 + dx/3.0, y0 + dy/3.0)
    b = (x0 + 2*dx/3.0, y0 + 2*dy/3.0)
    # Rotate (dx/3, dy/3) by +60 degrees around point a to get the 'peak'
    ux, uy = dx/3.0, dy/3.0
    cos60, sin60 = 0.5, math.sqrt(3)/2.0
    px = a[0] + ux*cos60 - uy*sin60
    py = a[1] + ux*sin60 + uy*cos60
    peak = (px, py)
    return [p0, a, peak, b, p1]

def koch_iter(points):
    """Apply one Koch iteration to a closed polyline (last==first)."""
    new_pts = []
    for i in range(len(points)-1):
        seg_points = koch_subdivide(points[i], points[i+1])
        new_pts.extend(seg_points[:-1])  # skip last to avoid duplicates
    new_pts.append(new_pts[0])  # close
    return new_pts

def generate_fractal(n_sides: int, side_len: float, depth: int):
    pts = regular_polygon(n_sides, side_len)
    for _ in range(depth):
        pts = koch_iter(pts)
    return pts

def write_points(points, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for x,y in points:
            f.write(f"{x:.6f},{y:.6f}\n")

def write_summary(n_sides, side_len, depth, points, out_path):
    # segments = n_sides * 4^depth
    segments = n_sides * (4 ** depth)
    # Each new segment length = side_len / 3^depth
    seg_len = side_len / (3 ** depth) if depth >= 0 else float('nan')
    # Approximate perimeter
    perimeter = segments * seg_len

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Koch Fractal Summary\n")
        f.write(f"Number of sides: {n_sides}\n")
        f.write(f"Side length: {side_len}\n")
        f.write(f"Depth: {depth}\n")
        f.write(f"Segments: {segments}\n")
        f.write(f"Segment length at depth: {seg_len}\n")
        f.write(f"Approx perimeter: {perimeter}\n")
        f.write(f"Points written: {len(points)}\n")

def save_plot(points, out_path):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available — skipping PNG plot. (Install with: python -m pip install matplotlib)")
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plt.figure()
    plt.plot(xs, ys)
    plt.axis('equal')
    plt.title("Koch Fractal")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Wrote {out_path}")

def parse_args():
    p = argparse.ArgumentParser(description="Q3: Recursive fractal generator (Koch-style).")
    p.add_argument("--sides", type=int, help="Number of sides (>=3).")
    p.add_argument("--length", type=float, help="Side length (e.g., 1.0).")
    p.add_argument("--depth", type=int, help="Recursion depth (>=0).")
    p.add_argument("--outdir", type=str, default=".", help="Output directory (default: current).")
    p.add_argument("--no-plot", action="store_true", help="Do not produce PNG even if matplotlib is installed.")
    return p.parse_args()

def prompt_int(prompt, min_val=None):
    while True:
        try:
            v = int(input(prompt).strip())
            if min_val is not None and v < min_val: raise ValueError()
            return v
        except Exception:
            print("Invalid input. Try again.")

def prompt_float(prompt):
    while True:
        try:
            return float(input(prompt).strip())
        except Exception:
            print("Invalid input. Try again.")

def main():
    args = parse_args()

    if args.sides is None:
        n_sides = prompt_int("Enter number of sides (>=3): ", min_val=3)
    else:
        n_sides = args.sides
        if n_sides < 3:
            print("Number of sides must be >= 3"); sys.exit(1)

    if args.length is None:
        side_len = prompt_float("Enter side length (e.g., 1.0): ")
    else:
        side_len = args.length

    if args.depth is None:
        depth = prompt_int("Enter recursion depth (>=0): ", min_val=0)
    else:
        depth = args.depth
        if depth < 0:
            print("Depth must be >= 0"); sys.exit(1)

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # Generate fractal
    pts = generate_fractal(n_sides, side_len, depth)

    # Write outputs
    points_path = os.path.join(outdir, "koch_points.txt")
    summary_path = os.path.join(outdir, "koch_summary.txt")
    write_points(pts, points_path)
    write_summary(n_sides, side_len, depth, pts, summary_path)
    print(f"Wrote {points_path}")
    print(f"Wrote {summary_path}")

    # Optional PNG
    if not args.no_plot:
        png_path = os.path.join(outdir, "koch_plot.png")
        save_plot(pts, png_path)

if __name__ == "__main__":
    main()
