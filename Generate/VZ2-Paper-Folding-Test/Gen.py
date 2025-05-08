import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
import os
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import LineString, Point
import random
import math
from shapely.affinity import rotate, translate


class EnhancedPaperFolder:
    def __init__(self, grid_size=6):
        """Initialize the paper folding simulator"""
        self.grid_size = grid_size
        # Initialize the paper as a square, represented by vertex coordinates
        self.paper = ShapelyPolygon([
            (0, 0), (grid_size, 0),
            (grid_size, grid_size), (0, grid_size)
        ])
        self.fold_count = 0
        self.output_dir = "folding_results"
        self.fold_history = []  # Record folding history

        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Save initial state
        self._draw_and_save()

    def fold(self, line_type, position):
        """
        Fold the paper along the specified line
        line_type: 'h'(horizontal), 'v'(vertical), 'd+'(diagonal with slope +1), 'd-'(diagonal with slope -1)
        position: position of the folding line
        Return: Whether the fold was successfully executed
        """
        # Calculate the folding line
        fold_line = self._get_fold_line(line_type, position)

        # If the folding line does not intersect the paper, do not fold
        if not fold_line.intersects(self.paper):
            print(f"The folding line does not intersect the paper, skipping fold")
            # Do not increase fold_count, do not record history, do not output PNG
            return False

        # Record folding history
        self.fold_history.append((line_type, position))
        self.fold_count += 1

        # Divide the paper into two parts: the stationary part and the part to be folded
        line_coords = list(fold_line.coords)
        # Extend the folding line to ensure it completely passes through the paper
        extended_line = self._extend_line(line_coords[0], line_coords[1])

        # Split the paper using the extended line
        split_result = self._split_polygon_by_line(self.paper, extended_line)

        if len(split_result) != 2:
            print(f"The folding line did not correctly split the paper, skipping fold #{self.fold_count}")
            self._draw_and_save()
            return False

        # Determine which part needs to be folded (usually the smaller part)
        part1, part2 = split_result
        if part1.area > part2.area:
            stationary_part, folding_part = part1, part2
        else:
            stationary_part, folding_part = part2, part1

        # Perform the fold (reflect folding_part along fold_line)
        folded_part = self._reflect_polygon(folding_part, fold_line)

        # Merge the two parts to form the new paper
        self.paper = stationary_part.union(folded_part)

        # Draw and save the result
        self._draw_and_save()
        return True

    def _get_fold_line(self, line_type, position):
        """
        Get the fold line based on line type and position

        Args:
            line_type: Type of fold line ('horizontal', 'vertical', 'diagonal')
            position: Position of the fold line

        Returns:
            LineString: LineString object representing the fold line
        """
        if line_type == 'horizontal':
            return LineString([(0, position), (self.grid_size, position)])
        elif line_type == 'vertical':
            return LineString([(position, 0), (position, self.grid_size)])
        elif line_type == 'diagonal':
            # 对角线折叠
            if position == 'up':  # 左下到右上
                return LineString([(0, 0), (self.grid_size, self.grid_size)])
            else:  # 左上到右下
                return LineString([(0, self.grid_size), (self.grid_size, 0)])
        else:
            # 处理随机折叠线
            return LineString(position)

    def _extend_line(self, p1, p2):
        """Extend the segment to ensure it is long enough to pass through the entire paper"""
        # Calculate direction vector
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        # Avoid division by zero
        if dx == 0 and dy == 0:
            return LineString([p1, p2])

        # Calculate extension factor (ensure the line is long enough)
        extension_factor = 2 * self.grid_size / max(abs(dx), abs(dy)) if max(abs(dx), abs(dy)) > 0 else 1

        # Calculate extended endpoints
        extended_p1 = (p1[0] - extension_factor * dx, p1[1] - extension_factor * dy)
        extended_p2 = (p2[0] + extension_factor * dx, p2[1] + extension_factor * dy)

        return LineString([extended_p1, extended_p2])

    def _split_polygon_by_line(self, polygon, line):
        """Split the polygon using a line"""
        # If the line does not intersect the polygon, return the original polygon
        if not line.intersects(polygon):
            return [polygon]

        # Get the coordinates of the polygon
        poly_coords = list(polygon.exterior.coords)

        # Get the coordinates of the line
        line_coords = list(line.coords)

        # Calculate the line equation Ax + By + C = 0
        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # Divide points into two groups based on their position relative to the line
        group1 = []
        group2 = []

        for point in poly_coords[:-1]:  # Exclude the last point (it repeats the first)
            # Calculate the signed distance from the point to the line
            x, y = point
            dist = (A * x + B * y + C) / np.sqrt(A ** 2 + B ** 2)

            if dist > 1e-10:  # Use a small threshold to handle numerical errors
                group1.append(point)
            elif dist < -1e-10:
                group2.append(point)
            else:  # Point is on the line, add to both groups
                group1.append(point)
                group2.append(point)

        # Calculate intersection points between the line and the polygon boundary
        intersections = []
        for i in range(len(poly_coords) - 1):
            edge = LineString([poly_coords[i], poly_coords[i + 1]])
            if line.intersects(edge):
                intersection = line.intersection(edge)
                if not intersection.is_empty:
                    if intersection.geom_type == 'Point':
                        intersections.append((intersection.x, intersection.y))
                    elif intersection.geom_type == 'MultiPoint':
                        for point in intersection.geoms:
                            intersections.append((point.x, point.y))

        # Remove duplicate intersection points
        unique_intersections = []
        for point in intersections:
            if point not in unique_intersections:
                unique_intersections.append(point)

        # If there are intersection points, add them to both groups
        if len(unique_intersections) >= 2:
            for point in unique_intersections:
                if point not in group1:
                    group1.append(point)
                if point not in group2:
                    group2.append(point)

        # Create two new polygons
        result = []
        if len(group1) >= 3:
            # Sort points to form a valid polygon
            group1 = self._sort_points_to_form_polygon(group1)
            poly1 = ShapelyPolygon(group1)
            if poly1.is_valid and poly1.area > 0:
                result.append(poly1)

        if len(group2) >= 3:
            # Sort points to form a valid polygon
            group2 = self._sort_points_to_form_polygon(group2)
            poly2 = ShapelyPolygon(group2)
            if poly2.is_valid and poly2.area > 0:
                result.append(poly2)

        return result

    def _sort_points_to_form_polygon(self, points):
        """Sort points to form a valid polygon"""
        # Calculate the center point
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)

        # Sort by angle relative to the center point
        def angle_to_center(point):
            return np.arctan2(point[1] - center_y, point[0] - center_x)

        sorted_points = sorted(points, key=angle_to_center)

        # Ensure the polygon is closed
        if sorted_points[0] != sorted_points[-1]:
            sorted_points.append(sorted_points[0])

        return sorted_points

    def _reflect_polygon(self, polygon, axis):
        """Reflect the polygon along the given axis"""
        # Get two points of the axis
        axis_coords = list(axis.coords)
        p1, p2 = axis_coords[0], axis_coords[1]

        # Calculate the direction vector of the axis
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        # Calculate the angle of the axis (relative to the x-axis)
        angle = np.arctan2(dy, dx) * 180 / np.pi

        # Translate the polygon so the axis passes through the origin
        translated_polygon = translate(polygon, -p1[0], -p1[1])

        # Rotate the polygon so the axis aligns with the x-axis
        rotated_polygon = rotate(translated_polygon, -angle, origin=(0, 0))

        # Reflect along the x-axis (i.e., invert the y-coordinate)
        reflected_coords = []
        for x, y in rotated_polygon.exterior.coords:
            reflected_coords.append((x, -y))

        reflected_polygon = ShapelyPolygon(reflected_coords)

        # Rotate back to the original angle
        rotated_back = rotate(reflected_polygon, angle, origin=(0, 0))

        # Translate back to the original position
        final_polygon = translate(rotated_back, p1[0], p1[1])

        return final_polygon

    def random_fold(self, num_folds=1):
        """
        Perform specified number of random folds

        Args:
            num_folds: Number of random folds to perform

        Returns:
            bool: Returns True if all folds are successful
        """
        print(f"Performing {num_folds} random folds...")

        for _ in range(num_folds):
            # 随机选择折叠线类型
            line_type = random.choice(['horizontal', 'vertical', 'diagonal', 'random'])

            if line_type == 'horizontal':
                # 随机选择水平折叠线的y坐标（只使用整数）
                position = random.randint(0, self.grid_size)
            elif line_type == 'vertical':
                # 随机选择垂直折叠线的x坐标（只使用整数）
                position = random.randint(0, self.grid_size)
            elif line_type == 'diagonal':
                # 随机选择对角线方向
                position = random.choice(['up', 'down'])
            else:  # 'random'
                # 随机生成两个点来定义折叠线
                # 确保点在纸张边界上或附近，并且坐标为整数
                boundary_points = []
                sides = [
                    [(0, y) for y in range(0, self.grid_size + 1)],  # 左边
                    [(self.grid_size, y) for y in range(0, self.grid_size + 1)],  # 右边
                    [(x, 0) for x in range(0, self.grid_size + 1)],  # 底边
                    [(x, self.grid_size) for x in range(0, self.grid_size + 1)]  # 顶边
                ]

                # 扁平化边界点列表
                all_boundary_points = [p for side in sides for p in side]

                # 随机选择两个不同的边界点
                while len(boundary_points) < 2:
                    point = random.choice(all_boundary_points)
                    if point not in boundary_points:
                        boundary_points.append(point)

                position = boundary_points

            # 尝试执行折叠
            if self.fold(line_type, position):
                # 折叠成功，绘制并保存当前状态
                self._draw_and_save()
            else:
                print(f"Fold failed: {line_type} at {position}")

        return True

    def punch_hole(self):
        """Randomly punch a hole in the paper, ensuring the hole is at the center of a grid cell"""
        # Ensure the paper exists
        if self.paper.is_empty:
            print("The paper does not exist, cannot punch a hole")
            return None

        # Get the bounding box of the paper
        minx, miny, maxx, maxy = self.paper.bounds

        # Create all possible grid cell center points
        possible_points = []
        for i in range(int(minx), int(maxx) + 1):
            for j in range(int(miny), int(maxy) + 1):
                # Center coordinates of the grid cell
                center_x = i + 0.5
                center_y = j + 0.5

                # Check if the point is within the paper
                if minx <= center_x <= maxx and miny <= center_y <= maxy:
                    possible_points.append((center_x, center_y))

        # Shuffle the possible points
        random.shuffle(possible_points)

        # Try each possible point
        for x, y in possible_points:
            point = Point(x, y)

            # Check if the point is inside the paper
            if self.paper.contains(point):
                # Draw and save the paper with a hole
                self._draw_hole(point)
                return (x, y)

        print("Cannot find a suitable position to punch a hole on the paper")
        return None

    def _draw_and_save(self):
        """Draw the current state of the paper and save as PNG"""
        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw the paper (white fill, black border)
        if self.paper.geom_type == 'Polygon':
            x, y = self.paper.exterior.xy
            ax.fill(x, y, fc='white', ec='black', linewidth=1.5)
        elif self.paper.geom_type == 'MultiPolygon':
            for geom in self.paper.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, fc='white', ec='black', linewidth=1.5)

        # Set figure properties
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')

        # Remove axes
        ax.axis('off')

        # Save image
        plt.savefig(os.path.join(self.output_dir, f'fold_{self.fold_count}.png'), bbox_inches='tight')
        plt.close()

    def _draw_hole(self, point):
        """Draw the paper with a hole"""
        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw the paper (white fill, black border)
        if self.paper.geom_type == 'Polygon':
            x, y = self.paper.exterior.xy
            ax.fill(x, y, fc='white', ec='black', linewidth=1.5)
        elif self.paper.geom_type == 'MultiPolygon':
            for geom in self.paper.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, fc='white', ec='black', linewidth=1.5)

        # Draw the hole (black hollow point)
        hole = Circle((point.x, point.y), 0.2, fc='white', ec='black', linewidth=1.5)
        ax.add_patch(hole)

        # Set figure properties
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')

        # Remove axes
        ax.axis('off')

        # Save image
        plt.savefig(os.path.join(self.output_dir, f'fold_{self.fold_count}_with_hole.png'), bbox_inches='tight')
        plt.close()

    def generate_interference_patterns(self, num_holes, num_patterns=4):
        """
        Generate interference patterns with the same number of holes but different positions
        
        Args:
            num_holes: Number of holes in the original pattern
            num_patterns: Number of interference patterns to generate
        """
        # Create initial square paper
        original_paper = ShapelyPolygon([
            (0, 0), (self.grid_size, 0),
            (self.grid_size, self.grid_size), (0, self.grid_size)
        ])

        # Generate all possible grid cell center points
        possible_points = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                center_x = i + 0.5
                center_y = j + 0.5
                possible_points.append((center_x, center_y))

        # Generate interference patterns
        for pattern_idx in range(num_patterns):
            # Randomly select points for holes
            selected_points = random.sample(possible_points, num_holes)
            
            # Draw pattern
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # Draw the paper (white fill, black border)
            x, y = original_paper.exterior.xy
            ax.fill(x, y, fc='white', ec='black', linewidth=1.5)
            
            # Draw holes
            for point in selected_points:
                hole = Circle(point, 0.2, fc='white', ec='black', linewidth=1.5)
                ax.add_patch(hole)
            
            # Set figure properties
            ax.set_xlim(-1, self.grid_size + 1)
            ax.set_ylim(-1, self.grid_size + 1)
            ax.set_aspect('equal')
            
            # Remove axes
            ax.axis('off')
            
            # Save image
            plt.savefig(os.path.join(self.output_dir, f'interference_pattern_{pattern_idx + 1}.png'), bbox_inches='tight')
            plt.close()

    def unfold_and_show_holes(self, hole_coords):
        """Unfold the paper and show all hole positions"""
        # Create initial square paper
        original_paper = ShapelyPolygon([
            (0, 0), (self.grid_size, 0),
            (self.grid_size, self.grid_size), (0, self.grid_size)
        ])

        # Convert hole coordinates to point
        hole = Point(hole_coords)

        # Apply fold history in reverse to calculate all hole positions on original paper
        all_holes = [hole]
        current_paper = self.paper

        # Traverse fold history in reverse
        for line_type, position in reversed(self.fold_history):
            # Calculate fold line
            fold_line = self._get_fold_line(line_type, position)

            # Find new hole positions
            new_holes = []
            for h in all_holes:
                # If hole is on one side of fold line, add its mirror on the other side
                if self._is_point_on_side(h, fold_line, current_paper):
                    mirrored_hole = self._mirror_point(h, fold_line)
                    new_holes.append(mirrored_hole)

            # Add newly discovered holes
            all_holes.extend(new_holes)

        # Filter out holes that are not on the original paper
        valid_holes = [h for h in all_holes if original_paper.contains(h)]

        # Draw original paper and all holes
        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw the original paper (white fill, black border)
        x, y = original_paper.exterior.xy
        ax.fill(x, y, fc='white', ec='black', linewidth=1.5)

        # Draw all holes (black hollow points)
        for h in valid_holes:
            hole = Circle((h.x, h.y), 0.2, fc='white', ec='black', linewidth=1.5)
            ax.add_patch(hole)

        # Set figure properties
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')

        # Remove axes
        ax.axis('off')

        # Save image
        plt.savefig(os.path.join(self.output_dir, 'unfolded_with_holes.png'), bbox_inches='tight')
        plt.close()

        # Generate interference patterns
        self.generate_interference_patterns(len(valid_holes))

        return valid_holes

    def _is_point_on_side(self, point, line, reference_shape):
        """
        Determine if a point is on one side of the line (same side as reference shape)

        Args:
            point: Point to check
            line: Fold line
            reference_shape: Reference shape to determine the "correct" side

        Returns:
            bool: Returns True if point is on the same side as reference shape
        """
        # Extract two points from the line
        p1, p2 = list(line.coords)[:2]

        # Calculate coefficients of line equation Ax + By + C = 0
        A = p2[1] - p1[1]  # y2 - y1
        B = p1[0] - p2[0]  # x1 - x2
        C = p2[0] * p1[1] - p1[0] * p2[1]  # x2*y1 - x1*y2

        # Calculate signed distance from point to line
        # Handle division by zero
        denominator = A ** 2 + B ** 2
        if denominator < 1e-10:  # If denominator is close to zero
            return False  # In this case, we cannot determine which side the point is on, return False to skip this point

        dist = (A * point.x + B * point.y + C) / math.sqrt(denominator)

        # Get a point on the reference shape (e.g., first vertex)
        if reference_shape.geom_type == 'Polygon':
            ref_point = Point(reference_shape.exterior.coords[0])
        else:  # MultiPolygon
            ref_point = Point(reference_shape.geoms[0].exterior.coords[0])

        # Calculate signed distance from reference point to line
        ref_dist = (A * ref_point.x + B * ref_point.y + C) / math.sqrt(denominator)

        # If signs of both distances are the same, point is on the same side as reference shape
        return (dist * ref_dist) > 0

    def _mirror_point(self, point, line):
        """
        Calculate the mirror point of a point across a line

        Args:
            point: Point to mirror
            line: Mirror line

        Returns:
            Point: Mirrored point
        """
        # Extract two points from the line
        p1, p2 = list(line.coords)[:2]

        # Calculate coefficients of line equation Ax + By + C = 0
        A = p2[1] - p1[1]  # y2 - y1
        B = p1[0] - p2[0]  # x1 - x2
        C = p2[0] * p1[1] - p1[0] * p2[1]  # x2*y1 - x1*y2

        # Handle division by zero
        denominator = A ** 2 + B ** 2
        if denominator < 1e-10:  # If denominator is close to zero
            return point  # Return original point to avoid error

        # Calculate signed distance from point to line
        dist = (A * point.x + B * point.y + C) / math.sqrt(denominator)

        # Calculate unit normal vector of the line
        nx = A / math.sqrt(denominator)
        ny = B / math.sqrt(denominator)

        # Calculate mirrored point coordinates
        mx = point.x - 2 * dist * nx
        my = point.y - 2 * dist * ny

        return Point(mx, my)


# Usage example
if __name__ == "__main__":
    # Create the paper folding simulator
    folder = EnhancedPaperFolder(grid_size=6)

    # Perform random folds
    num_folds = random.randint(1,3)
    print(f"Performing {num_folds} random folds...")
    folder.random_fold(num_folds)

    # Punch a hole
    print("Randomly punching a hole on the paper...")
    hole_coords = folder.punch_hole()

    if hole_coords:
        print(f"Hole coordinates: {hole_coords}")

        # Unfold and show all holes
        print("Unfolding the paper and showing all holes...")
        all_holes = folder.unfold_and_show_holes(hole_coords)
        print(f"There are {len(all_holes)} holes after unfolding")
    else:
        print("Failed to punch a hole")
