import cv2
import numpy as np
import random
import math
import os
import json

def generate_grid_image(image_number, output_dir):
    # Set image size - increase resolution
    width_5x5 = 600  # Increase width
    height_5x5 = 600  # Increase height
    total_width = width_5x5 * 2 + 100  # Two 5x5 grids with 100 pixels of spacing

    # Create a blank image (white background)
    img = np.ones((height_5x5, total_width, 3), np.uint8) * 255  # 3 channels, white

    # Set point size and color - adjust for new resolution
    dot_size = 15  # Increase point size
    dot_color = (0, 0, 0)  # Black
    line_color = (0, 0, 0)  # Black lines
    line_thickness = 3  # Increase line thickness

    # Calculate spacing between points in the 5x5 grid
    x_spacing_5x5 = width_5x5 // 5
    y_spacing_5x5 = height_5x5 // 5

    # Create point coordinate list for the left 5x5 grid (not drawing points, but needed for lines)
    points_left = []
    for i in range(5):  # i is the row index (y coordinate)
        for j in range(5):  # j is the column index (x coordinate)
            x = x_spacing_5x5 * j + x_spacing_5x5 // 2
            y = y_spacing_5x5 * i + y_spacing_5x5 // 2
            points_left.append((x, y))

    # Create point coordinate list for the right 5x5 grid
    points_right = []
    for i in range(5):
        for j in range(5):
            x = width_5x5 + 100 + x_spacing_5x5 * j + x_spacing_5x5 // 2  # Add offset
            y = y_spacing_5x5 * i + y_spacing_5x5 // 2
            points_right.append((x, y))

    # Draw points on the right 5x5 grid
    for i, (x, y) in enumerate(points_right):
        cv2.circle(img, (x, y), dot_size // 2, dot_color, -1)

    # Randomly select a starting point
    start_index = random.randint(0, 24)
    start_point = points_left[start_index]
    print(f"Image {image_number}: Starting point is point {start_index + 1}")

    # Generate random segments
    num_segments = random.randint(4, 6)
    current_point = start_point
    current_index = start_index
    visited_indices = {start_index}  # Record visited point indices
    path = [current_point]  # Record all points in the path
    path_indices = [current_index]  # Record all point indices in the path

    def gcd(a, b):
        """Calculate the greatest common divisor"""
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a

    def are_coprime(a, b):
        """Check if two numbers are coprime (GCD is 1)"""
        if a == 0 and b == 0:  # Special case: 0 and 0 are not coprime
            return False
        return gcd(a, b) == 1

    def get_coprime_moves(row, col):
        """Get all possible coprime moves"""
        moves = []
        # Consider movements within a reasonable range
        for i in range(-4, 5):  # From -4 to 4
            for j in range(-4, 5):  # From -4 to 4
                # Skip the case of staying in the same place
                if i == 0 and j == 0:
                    continue

                # Check if i and j are coprime
                if are_coprime(i, j):
                    new_row, new_col = row + i, col + j
                    # Ensure the new position is within the 5x5 grid
                    if 0 <= new_row < 5 and 0 <= new_col < 5:
                        moves.append((new_row, new_col))
        return moves

    for _ in range(num_segments):
        # Get current point's row and column indices
        current_row, current_col = divmod(current_index, 5)

        # Get all possible coprime moves
        possible_moves = get_coprime_moves(current_row, current_col)

        # Convert to point indices and filter out visited points
        possible_next_indices = []
        for row, col in possible_moves:
            idx = row * 5 + col
            if idx not in visited_indices:
                possible_next_indices.append(idx)

        if not possible_next_indices:  # If no feasible moves, end loop
            print(f"Image {image_number}: No feasible coprime moves, ending connection.")
            break

        # Randomly select an unvisited point
        next_index = random.choice(possible_next_indices)
        next_point = points_left[next_index]
        path.append(next_point)  # Add to path
        path_indices.append(next_index)  # Add index to path

        # Update current point and index
        current_point = next_point
        current_index = next_index
        visited_indices.add(next_index)  # Add new point to visited set

        # Calculate i and j values for debugging
        next_row, next_col = divmod(next_index, 5)
        i, j = next_row - current_row, next_col - current_col
        print(f"Image {image_number}: Connected to point {next_index + 1}, moved ({i},{j})")

    # Draw path lines on the left grid
    for i in range(len(path) - 1):
        cv2.line(img, path[i], path[i+1], line_color, line_thickness)

    # Mark the starting point on the left 5x5 grid
    cv2.circle(img, start_point, dot_size, (0, 0, 0), 2)  # Black circle
    cv2.circle(img, start_point, dot_size // 2, dot_color, -1)  # Add black dot at the center

    # Mark the same relative starting point on the right 5x5 grid
    start_point_right = points_right[start_index]

    # Draw a circle around the starting point on the right grid and add a dot at the center
    cv2.circle(img, start_point_right, dot_size, (0, 0, 0), 2)  # Black circle
    cv2.circle(img, start_point_right, dot_size // 2, dot_color, -1)  # Add black dot at the center

    # Save image - use higher quality save settings
    filename = f"{image_number}.png"
    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print(f"Saved image: {output_path}")

    # Return the endpoint index (1-based indexing)
    end_index = path_indices[-1] + 1  # Add 1 because we want to start counting from 1
    return output_path, end_index

# Main program
def main():
    try:
        num_images = int(input("Enter the number of images to generate: "))
        if num_images <= 0:
            print("Please enter a number greater than 0")
            return

        # Create the Images directory if it doesn't exist
        if not os.path.exists("Images"):
            os.makedirs("Images")

        # Create or overwrite ans.txt file
        with open("ans.txt", "w") as f:
            for i in range(num_images):
                img_path, end_index = generate_grid_image(i, "Images")
                # Write the endpoint to ans.txt
                f.write(f"({(end_index-1) // 5 + 1}, {((end_index-1) % 5)+1})\n")

        print(f"Successfully generated {num_images} images, from 0.png to {num_images - 1}.png")
        print(f"All endpoints written to ans.txt")

        # Create JSON data with nested lists
        questions = [[os.path.join("Images", f"{i}.png")] for i in range(num_images)]
        with open("ans.txt", "r") as f:
            answers = [[line.strip()] for line in f.readlines()]

        json_data = {
            "Questions": questions,
            "Answers": answers
        }

        # Save JSON data to file
        with open("questions_answers.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        print("JSON file 'questions_answers.json' created successfully.")

    except ValueError:
        print("Please enter a valid number")

if __name__ == "__main__":
    main()