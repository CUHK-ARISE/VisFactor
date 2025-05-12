import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
import matplotlib.patches as patches
import random
import os
import json

# 创建必要的目录
def create_directories():
    base_dir = "Images/CF1-Hidden-Figures-Test"
    split_dir = os.path.join(base_dir, "Split")
    os.makedirs(split_dir, exist_ok=True)
    return base_dir, split_dir

# Part 1: Generate 5 simple closed shapes
def generate_simple_shape(image_index, grid_size=4, fill_shapes=False, output_dir="Images/CF1-Hidden-Figures-Test/Split"):
    """
    Generate a simple closed shape and save it as a PNG file.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-0.5, grid_size-0.5)
    ax.set_ylim(-0.5, grid_size-0.5)

    grid_points = np.array([(x, y) for x in range(grid_size) for y in range(grid_size)])
    num_vertices = np.random.randint(4, 8)
    indices = np.random.choice(len(grid_points), size=num_vertices, replace=False)
    vertices = grid_points[indices]

    centroid = np.mean(vertices, axis=0)
    angles = np.arctan2(vertices[:, 1] - centroid[1], vertices[:, 0] - centroid[0])
    vertices = vertices[np.argsort(angles)]
    vertices = np.vstack([vertices, vertices[0]])

    if fill_shapes:
        codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 2) + [Path.CLOSEPOLY]
        path = Path(vertices, codes)
        patch = patches.PathPatch(path, facecolor='lightgray', edgecolor='black', linewidth=2)
        ax.add_patch(patch)
    else:
        for i in range(len(vertices)-1):
            ax.plot([vertices[i][0], vertices[i+1][0]],
                    [vertices[i][1], vertices[i+1][1]],
                    'k-', linewidth=2)

    ax.set_axis_off()
    output_path = os.path.join(output_dir, f'0-{image_index}.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    return vertices

# Function to create a random closed shape
def create_random_closed_shape(grid_size):
    num_points = random.randint(3, 6)
    points = []
    for _ in range(num_points):
        x = random.randint(0, grid_size-1)
        y = random.randint(0, grid_size-1)
        points.append((x, y))

    unique_points = list(set(points))
    while len(unique_points) < 3:
        x = random.randint(0, grid_size-1)
        y = random.randint(0, grid_size-1)
        pt = (x, y)
        if pt not in unique_points:
            unique_points.append(pt)

    vertices = np.array(unique_points)
    centroid = np.mean(vertices, axis=0)
    angles = np.arctan2(vertices[:, 1] - centroid[1], vertices[:, 0] - centroid[0])
    vertices = vertices[np.argsort(angles)]
    vertices = np.vstack([vertices, vertices[0]])
    return vertices

# Part 2: Generate a complex image
def generate_complex_image(image_index, simple_shapes, grid_size=6, fill_original_shapes=False, output_dir="Images/CF1-Hidden-Figures-Test/Split"):
    """
    Generate a complex image by placing 1 simple shape on a large canvas,
    and adding 3–7 distraction closed shapes.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-0.5, grid_size-0.5)
    ax.set_ylim(-0.5, grid_size-0.5)

    # Select only 1 original simple shape
    chosen_idx = random.randrange(len(simple_shapes))
    vertices = simple_shapes[chosen_idx]

    # Random offset
    max_offset = grid_size - 4
    offset_x = random.randint(0, max_offset)
    offset_y = random.randint(0, max_offset)
    shifted = vertices.copy()
    shifted[:, 0] += offset_x
    shifted[:, 1] += offset_y

    # Draw the simple shape
    if fill_original_shapes:
        codes = [Path.MOVETO] + [Path.LINETO] * (len(shifted) - 2) + [Path.CLOSEPOLY]
        path = Path(shifted, codes)
        patch = patches.PathPatch(path, facecolor='lightgray', edgecolor='black', linewidth=2)
        ax.add_patch(patch)
    else:
        for i in range(len(shifted)-1):
            ax.plot([shifted[i][0], shifted[i+1][0]],
                    [shifted[i][1], shifted[i+1][1]],
                    'k-', linewidth=2)

    # Add 3–7 distraction polygons
    num_distraction_shapes = random.randint(3, 7)
    for _ in range(num_distraction_shapes):
        disp = create_random_closed_shape(grid_size)
        for i in range(len(disp)-1):
            ax.plot([disp[i][0], disp[i+1][0]],
                    [disp[i][1], disp[i+1][1]],
                    'k-', linewidth=2)

    ax.set_axis_off()
    output_path = os.path.join(output_dir, f'{image_index}.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

    return chosen_idx

def generate_meta_json(simple_shapes_count=5, complex_images_count=30, used_shapes=None):
    meta = {
        "CF1": {
            "Name": "Hidden-Figures-Test",
            "Example": [
                ["Text", "Now try this example."],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/1.jpg"],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/2.jpg"],
                ["Text", "The answer is A. The figure below shows how figure A is included in the pattern."],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/4.jpg"],
                ["Text", "Now try this example."],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/1.jpg"],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/3.jpg"],
                ["Text", "The answer is D. The figure below shows how figure D is included in the pattern."],
                ["Image", "../Images/CF1-Hidden-Figures-Test/Example/5.jpg"]
            ],
            "Group": {
                "Description": "This is a test of your ability to tell whether a sample figure can be found in a more complex pattern. You will first see one simple figure. Then you will see a figure of the complex pattern. NOTE: If the figure is in the complex pattern, it will always be right side up and exactly the same size with the simple figure. You are to decide whether the first image can be found in the second image.",
                "Instruction": "For the question below: Please provide your answer in the following JSON format: {\"answer\": \"yes_or_no\"}.",
                "Answers": [],
                "Questions": []
            }
        }
    }

    # Generate questions and answers
    for i in range(1, complex_images_count + 1):
        for j in range(simple_shapes_count):
            meta["CF1"]["Group"]["Questions"].append([
                f"Images/CF1-Hidden-Figures-Test/Split/0-{j}.png",
                f"Images/CF1-Hidden-Figures-Test/Split/{i}.png"
            ])
            # 根据使用的简单图形生成答案
            answer = "yes" if used_shapes[i-1] == j else "no"
            meta["CF1"]["Group"]["Answers"].append([answer])

    return meta

# Main program
def main():
    # Create necessary directories
    base_dir, split_dir = create_directories()
    
    # Generate simple shapes
    simple_shapes = []
    for i in range(5):
        v = generate_simple_shape(i, fill_shapes=False, output_dir=split_dir)
        simple_shapes.append(v)
        print(f"Generated 0-{i}.png")

    # Generate complex images and record used shapes
    used_shapes = []
    for i in range(1, 31):
        used = generate_complex_image(i, simple_shapes, fill_original_shapes=False, output_dir=split_dir)
        used_shapes.append(used)
        print(f"Generated {i}.png, using simple shape: 0-{used}.png")

    # Generate meta.json with correct answers
    meta = generate_meta_json(used_shapes=used_shapes)
    with open("./meta.json", "w") as f:
        json.dump(meta, f, indent=4)
    print("Generated meta.json")

if __name__ == "__main__":
    main()