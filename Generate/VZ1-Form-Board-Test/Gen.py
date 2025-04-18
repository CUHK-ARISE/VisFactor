import math
import numpy as np
import matplotlib.pyplot as plt
import os


def plot_region_centered(region, vertex_coords, filename):
    """
    Draw a region (polygon) centered based on the vertex coordinates in region,
    and save the result to filename.
    """
    coords = [vertex_coords[v] for v in region]
    # Automatically close the polygon
    coords.append(vertex_coords[region[0]])
    xs, ys = zip(*coords)
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    centerx = (minx + maxx) / 2
    centery = (miny + maxy) / 2
    width = maxx - minx
    height = maxy - miny
    margin = max(width, height) * 0.2

    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, marker='o')
    plt.fill(xs, ys, alpha=0.3)
    plt.xlim(centerx - (width / 2 + margin), centerx + (width / 2 + margin))
    plt.ylim(centery - (height / 2 + margin), centery + (height / 2 + margin))
    plt.gca().set_aspect('equal', 'box')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def plot_polygon(polygon, vertex_coords, filename):
    """
    Draw the complete polygon and save it as an image.
    """
    coords = [vertex_coords[v] for v in polygon]
    # Close the polygon by adding the first vertex again
    coords.append(vertex_coords[polygon[0]])
    xs, ys = zip(*coords)
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, marker='o')
    plt.fill(xs, ys, alpha=0.3)
    plt.gca().set_aspect('equal', 'box')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def create_distractor(region, vertex_coords, distortion_type):
    """
    Create distractors: change the shape of the figure without adding new vertices.

    distortion_type:
        1 = Move all vertices (90% chance to shift each vertex, shift range [-8, 8]);
        2 = Remove some vertices and move (randomly remove some vertices and apply larger shifts to the remaining vertices, range [-12, 12]).

    Returns: (deformed region vertex sequence, new vertex coordinates dictionary)
    """
    new_coords = vertex_coords.copy()

    if distortion_type == 1:
        # Move each vertex in the region with a 90% chance, shift range [-8, 8]
        new_region = []
        for v in region:
            new_region.append(v)
            if np.random.random() < 0.9:  # 90% chance to move this vertex
                x, y = new_coords[v]
                new_coords[v] = (x + np.random.uniform(-8, 8),
                                 y + np.random.uniform(-8, 8))
        return new_region, new_coords

    elif distortion_type == 2:
        # Do not delete the first vertex to ensure closure; randomly delete other vertices (ensure at least 3 vertices remain)
        new_region = region.copy()
        for v in region[1:]:
            if len(new_region) > 3 and np.random.random() < 0.3:
                new_region.remove(v)
        # Apply larger shifts to all remaining vertices, range [-12, 12]
        for v in new_region:
            x, y = new_coords[v]
            new_coords[v] = (x + np.random.uniform(-12, 12),
                             y + np.random.uniform(-12, 12))
        return new_region, new_coords

    return region, new_coords


def random_partition_polygon(polygon):
    """
    Randomly partition the polygon into three regions:
    Steps:
      1. Randomly select a vertex as the starting point and "rotate" the polygon;
      2. In the rotated polygon, randomly select two indices from position 2 to n-2 (excluding neighbors of the starting vertex);
      3. Use these two lines to divide the original polygon into three regions.

    Returns: (region1, region2, region3), where each region is a list of vertex indices.
    """
    n = len(polygon)
    # Randomly select rotation starting point
    r = np.random.randint(0, n)
    rotated = polygon[r:] + polygon[:r]

    if n < 5:
        raise ValueError("Too few vertices to partition into three regions")

    # Allowed indices are [2, n-2] (excluding index 1 and index n-1)
    allowed = list(range(2, n - 1))
    i, j = np.random.choice(allowed, 2, replace=False)
    i, j = sorted([i, j])

    # Partition regions:
    # region1: from the starting vertex to the i-th vertex in the rotated polygon (inclusive)
    region1 = rotated[0:i + 1]
    # region2: from the i-th vertex to the j-th vertex in the rotated polygon, plus the starting vertex to ensure closure
    region2 = rotated[i:j + 1] + [rotated[0]]
    # region3: from the j-th vertex to the end, plus the starting vertex to ensure closure
    region3 = rotated[j:] + [rotated[0]]

    return region1, region2, region3


def ensure_dir(directory):
    """Create directory if it does not exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    # Define the number of groups to generate
    num_groups = int(input("Enter the number of groups to generate:\n"))  # Adjust the number of groups as needed
    out_dir = "output_images"
    ensure_dir(out_dir)

    # Lines to save in the answer file, each line corresponding to 5 images excluding the original figure
    ans_lines = []

    # Generate images for each group
    for group in range(1, num_groups + 1):
        # -----------------------
        # 1. Generate the original closed polygon
        n = 8  # Number of vertices, can be adjusted
        angles = sorted(np.random.uniform(0, 2 * np.pi, n))
        radii = np.random.uniform(8, 12, n)  # Random radii

        vertex_coords = {}
        for i, (angle, r) in enumerate(zip(angles, radii), start=1):
            vertex_coords[i] = (r * math.cos(angle), r * math.sin(angle))
        # List of original polygon vertices in angle order
        initial_polygon = list(vertex_coords.keys())

        # Save the original figure (i-0.png)
        file_original = os.path.join(out_dir, f"{group}-0.png")
        plot_polygon(initial_polygon, vertex_coords, file_original)

        # -----------------------
        # 2. Randomly partition the original polygon into three regions (all correct regions, label yes)
        region1, region2, region3 = random_partition_polygon(initial_polygon)
        regions_clean = [region1, region2, region3]  # Keep original regions (unmodified)

        # -----------------------
        # 3. Generate two distractors: randomly select 2 of the three regions to distort (label no)
        distractor_indices = np.random.choice([0, 1, 2], size=2, replace=False)
        distractors = []
        for idx in distractor_indices:
            # Randomly choose a distortion type: 1 or 2
            distortion_type = np.random.choice([1, 2])
            dist_region, dist_coords = create_distractor(regions_clean[idx], vertex_coords, distortion_type)
            distractors.append((dist_region, dist_coords))

        # -----------------------
        # 4. Prepare to save 5 images: 3 partitioned regions (correct) and 2 distractors (incorrect)
        # Shuffle these five items to prevent fixed order
        image_list = []
        # Correct regions, state "yes"
        for reg in regions_clean:
            image_list.append((reg, vertex_coords.copy(), "yes"))
        # Distractor regions, state "no"
        for reg, v_coords in distractors:
            image_list.append((reg, v_coords, "no"))

        np.random.shuffle(image_list)

        # Now output 5 images, filenames group-i-1.png to group-i-5.png
        for idx, (reg, coords, label) in enumerate(image_list, start=1):
            file_out = os.path.join(out_dir, f"{group}-{idx}.png")
            plot_region_centered(reg, coords, file_out)
            ans_lines.append(label)

    # Write answers to ans.txt file, one answer per line, total 5*num_groups lines
    with open(os.path.join(out_dir, "ans.txt"), "w", encoding="utf-8") as f:
        for line in ans_lines:
            f.write(line + "\n")


if __name__ == "__main__":
    main()