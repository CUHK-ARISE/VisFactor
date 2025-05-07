import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import random
import math
import os # For creating output directory

class GridPaperSimulatorStyled:
    """
    Simulates folding, punching, and unfolding of a grid-based paper.
    Uses 0-based indexing (0 to size-1).
    Visualizes internal grid lines, current boundaries, and folds.
    Outputs steps to PNG files.
    """
    def __init__(self, size=6, output_dir="folding_steps"):
        if size <= 0 or not isinstance(size, int):
            raise ValueError("Size must be a positive integer.")
        self.size = size
        self.is_valid = np.ones((size, size), dtype=bool)
        self.paper_layers = [[deque([(r, c)]) for c in range(size)] for r in range(size)]
        self.folds = [] # List: (axis, line_coord, folded_side)
        self.hole_location_folded = None # (row, col)
        self.holes_unfolded = np.zeros((size, size), dtype=bool)

        # --- Output setup ---
        self.output_dir = output_dir
        self.step_counter = 0
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
        else:
             # Clear previous files if needed (optional)
             # for f in os.listdir(self.output_dir):
             #     os.remove(os.path.join(self.output_dir, f))
             pass


        print(f"Initialized a {size}x{size} grid paper. Outputting steps to '{self.output_dir}/'")
        self._plot_state("Step 0: Initial Grid Paper")

    def get_current_bounds(self):
        """Finds the min/max row/col indices of valid cells."""
        rows, cols = np.where(self.is_valid)
        if len(rows) == 0:
            return None
        return rows.min(), rows.max(), cols.min(), cols.max()

    def _plot_state(self, title):
        """Plots the current state and saves to PNG."""
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title(title, fontsize=12)
        self.step_counter += 1
        filename = os.path.join(self.output_dir, f"step_{self.step_counter:02d}_{title.replace(' ', '_').replace(':', '').replace('=', '').replace('(','').replace(')','')}.png")

        line_color_internal = 'lightgrey'
        line_color_boundary = 'black'
        line_width_internal = 0.5
        line_width_boundary = 1.5

        # --- Draw Grid Lines and Boundaries ---
        for r in range(self.size + 1):
            for c in range(self.size):
                # Horizontal segment at row r, between column c and c+1
                # Check cells above (r-1, c) and below (r, c)
                is_above_valid = self.is_valid[r - 1, c] if 0 <= r - 1 < self.size else False
                is_below_valid = self.is_valid[r, c] if 0 <= r < self.size else False

                color = line_color_boundary if is_above_valid != is_below_valid else line_color_internal
                width = line_width_boundary if is_above_valid != is_below_valid else line_width_internal
                # Ensure original top/bottom edges are bold if adjacent cell is valid
                if (r == 0 and is_below_valid) or (r == self.size and is_above_valid):
                     color = line_color_boundary
                     width = line_width_boundary


                # Don't draw internal grey lines outside the current visual bounds for clarity (optional)
                # bounds = self.get_current_bounds()
                # draw_internal = True
                # if bounds and color == line_color_internal:
                #      min_r, max_r, min_c, max_c = bounds
                #      # Check if the line segment is roughly within the valid area
                #      if not (min_r <= r <= max_r + 1 and min_c <= c <= max_c):
                #           draw_internal = False

                # if color == line_color_boundary or draw_internal:
                ax.plot([c, c + 1], [r, r], color=color, lw=width, solid_capstyle='butt')


        for c in range(self.size + 1):
            for r in range(self.size):
                # Vertical segment at column c, between row r and r+1
                # Check cells left (r, c-1) and right (r, c)
                is_left_valid = self.is_valid[r, c - 1] if 0 <= c - 1 < self.size else False
                is_right_valid = self.is_valid[r, c] if 0 <= c < self.size else False

                color = line_color_boundary if is_left_valid != is_right_valid else line_color_internal
                width = line_width_boundary if is_left_valid != is_right_valid else line_width_internal
                # Ensure original left/right edges are bold if adjacent cell is valid
                if (c == 0 and is_right_valid) or (c == self.size and is_left_valid):
                    color = line_color_boundary
                    width = line_width_boundary

                # Optional: Filter internal lines like above
                # bounds = self.get_current_bounds()
                # draw_internal = True
                # if bounds and color == line_color_internal:
                #      min_r, max_r, min_c, max_c = bounds
                #      if not (min_r <= r <= max_r and min_c <= c <= max_c + 1):
                #           draw_internal = False

                # if color == line_color_boundary or draw_internal:
                ax.plot([c, c], [r, r + 1], color=color, lw=width, solid_capstyle='butt')

        # --- Draw Fold Lines ---
        for axis, line_coord, _ in self.folds:
            if axis == 'h': # Horizontal fold line at y = line_coord
                 ax.plot([0, self.size], [line_coord, line_coord], 'r--', lw=1.5, label='_nolegend_')
            else: # axis == 'v', Vertical fold line at x = line_coord
                 ax.plot([line_coord, line_coord], [0, self.size], 'r--', lw=1.5, label='_nolegend_')
        # Add legend entry for folds if any exist
        if self.folds:
             ax.plot([], [], 'r--', lw=1.5, label='Fold Line')


        # --- Show Punched Hole Location ---
        if self.hole_location_folded:
            r, c = self.hole_location_folded
            ax.plot(c + 0.5, r + 0.5, 'ko', markersize=8, mfc='black', label=f'Punched at ({r},{c})') # mfc='none' for hollow

        # --- Final Plot Setup ---
        ax.set_xlim(-0.5, self.size + 0.5)
        ax.set_ylim(-0.5, self.size + 0.5)
        ax.invert_yaxis() # Match matrix indexing (origin top-left)
        ax.set_aspect('equal', adjustable='box')
        plt.xlabel("Column Index")
        plt.ylabel("Row Index")
        plt.xticks(np.arange(self.size + 1))
        plt.yticks(np.arange(self.size + 1))
        plt.grid(False) # Turn off default grid
        if self.folds or self.hole_location_folded:
             ax.legend(fontsize=8, loc='upper right')

        # --- Save and Close ---
        try:
            plt.savefig(filename)
            print(f"Saved state to {filename}")
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
        plt.close(fig) # Close the figure to free memory

    def _plot_unfolded(self):
        """Plots the final unfolded paper with holes and saves to PNG."""
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title("Final Unfolded Paper with Holes", fontsize=12)
        filename = os.path.join(self.output_dir, "final_unfolded_paper.png")

        line_color_internal = 'lightgrey'
        line_color_boundary = 'black'
        line_width_internal = 0.5
        line_width_boundary = 1.5

        # Draw internal grid lines
        for i in range(1, self.size):
            ax.axhline(i, color=line_color_internal, lw=line_width_internal)
            ax.axvline(i, color=line_color_internal, lw=line_width_internal)

        # Draw outer boundary
        ax.add_patch(patches.Rectangle((0, 0), self.size, self.size,
                                       linewidth=line_width_boundary, edgecolor=line_color_boundary, facecolor='none'))

        # Show final hole locations
        hole_rows, hole_cols = np.where(self.holes_unfolded)
        if len(hole_rows) > 0:
            ax.plot(hole_cols + 0.5, hole_rows + 0.5, 'ro', markersize=8, mfc='red', label=f'{len(hole_rows)} Holes') # mfc='none' for hollow
            ax.legend(fontsize=8)

        # Final Plot Setup
        ax.set_xlim(-0.5, self.size + 0.5)
        ax.set_ylim(-0.5, self.size + 0.5)
        ax.invert_yaxis()
        ax.set_aspect('equal', adjustable='box')
        plt.xlabel("Column Index")
        plt.ylabel("Row Index")
        plt.xticks(np.arange(self.size + 1))
        plt.yticks(np.arange(self.size + 1))
        plt.grid(False)

        # Save and Close
        try:
            plt.savefig(filename)
            print(f"Saved final unfolded state to {filename}")
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
        plt.close(fig)

    # --- Methods for folding, punching, unfolding (largely unchanged) ---

    def get_valid_folds(self):
        """Returns a list of possible valid folds: [(axis, line_coord), ...]."""
        bounds = self.get_current_bounds()
        if bounds is None:
            return []
        min_r, max_r, min_c, max_c = bounds
        valid_folds = []

        for r_line in range(min_r + 1, max_r + 1):
             if np.any(self.is_valid[min_r:r_line, min_c:max_c+1]) and \
                np.any(self.is_valid[r_line:max_r+1, min_c:max_c+1]):
                 valid_folds.append(('h', r_line))

        for c_line in range(min_c + 1, max_c + 1):
             if np.any(self.is_valid[min_r:max_r+1, min_c:c_line]) and \
                np.any(self.is_valid[min_r:max_r+1, c_line:max_c+1]):
                 valid_folds.append(('v', c_line))
        return valid_folds

    def fold(self, axis, line_coord):
        """Performs a fold along the specified axis and line coordinate."""
        bounds = self.get_current_bounds()
        if bounds is None:
            print("Error: Cannot fold, no valid paper area left.")
            return False
        min_r, max_r, min_c, max_c = bounds

        is_valid_choice = False
        if axis == 'h' and min_r < line_coord <= max_r:
             if np.any(self.is_valid[min_r:line_coord, min_c:max_c+1]) and \
                np.any(self.is_valid[line_coord:max_r+1, min_c:max_c+1]):
                  is_valid_choice = True
        elif axis == 'v' and min_c < line_coord <= max_c:
             if np.any(self.is_valid[min_r:max_r+1, min_c:line_coord]) and \
                np.any(self.is_valid[min_r:max_r+1, line_coord:max_c+1]):
                  is_valid_choice = True

        if not is_valid_choice:
            print(f"Error: Fold {axis}={line_coord} is not valid or does not split the current paper shape.")
            return False

        fold_away_indices = None
        target_indices_func = None
        folded_side_label = ""

        if axis == 'h':
            height_top = line_coord - min_r
            height_bottom = (max_r + 1) - line_coord
            if height_top <= height_bottom:
                fold_away_rows = range(min_r, line_coord)
                target_row_func = lambda r: 2 * line_coord - 1 - r
                fold_away_indices = [(r, c) for r in fold_away_rows for c in range(min_c, max_c + 1)]
                target_indices_func = lambda r, c: (target_row_func(r), c)
                folded_side_label = "top"
            else:
                fold_away_rows = range(line_coord, max_r + 1)
                target_row_func = lambda r: 2 * line_coord - 1 - r
                fold_away_indices = [(r, c) for r in fold_away_rows for c in range(min_c, max_c + 1)]
                target_indices_func = lambda r, c: (target_row_func(r), c)
                folded_side_label = "bottom"
        else: # axis == 'v'
            width_left = line_coord - min_c
            width_right = (max_c + 1) - line_coord
            if width_left <= width_right:
                fold_away_cols = range(min_c, line_coord)
                target_col_func = lambda c: 2 * line_coord - 1 - c
                fold_away_indices = [(r, c) for r in range(min_r, max_r + 1) for c in fold_away_cols]
                target_indices_func = lambda r, c: (r, target_col_func(c))
                folded_side_label = "left"
            else:
                fold_away_cols = range(line_coord, max_c + 1)
                target_col_func = lambda c: 2 * line_coord - 1 - c
                fold_away_indices = [(r, c) for r in range(min_r, max_r + 1) for c in fold_away_cols]
                target_indices_func = lambda r, c: (r, target_col_func(c))
                folded_side_label = "right"

        print(f"Performing Fold {len(self.folds) + 1}: axis={axis}, line={line_coord}, folding {folded_side_label} part.")
        for r_from, c_from in fold_away_indices:
            if self.is_valid[r_from, c_from]:
                r_to, c_to = target_indices_func(r_from, c_from)
                if 0 <= r_to < self.size and 0 <= c_to < self.size:
                     layers_to_move = self.paper_layers[r_from][c_from]
                     self.paper_layers[r_to][c_to].extend(layers_to_move)
                     self.paper_layers[r_from][c_from].clear()
                     self.is_valid[r_from, c_from] = False
                else:
                     print(f"Warning: Calculated target ({r_to},{c_to}) for source ({r_from},{c_from}) is out of bounds.")

        self.folds.append((axis, line_coord, folded_side_label))
        self._plot_state(f"After Fold {len(self.folds)} ({axis}={line_coord} fold {folded_side_label})")
        return True

    def get_valid_punch_locations(self):
        """Returns a list of valid (row, col) coordinates for punching."""
        rows, cols = np.where(self.is_valid)
        return list(zip(rows, cols))

    def punch_hole(self, row, col):
        """Punches a hole at the center of the specified cell (row, col)."""
        if not self.is_valid[row, col]:
             print(f"Error: Cannot punch at ({row},{col}). Cell is not valid.")
             return False
        print(f"Punching hole at cell ({row}, {col}).")
        self.hole_location_folded = (row, col)
        self._plot_state("Paper with Hole Punched")
        return True

    def unfold(self):
        """Calculates the final hole pattern based on the folded hole location."""
        if self.hole_location_folded is None:
            print("No hole was punched. Nothing to unfold.")
            if self.folds:
                 self._plot_state(f"Final Folded State (No Hole)")
            else:
                 self._plot_state("Initial State (No Folds or Punch)")
            self._plot_unfolded() # Plot empty unfolded grid
            return

        punch_r, punch_c = self.hole_location_folded
        layers_at_punch_location = self.paper_layers[punch_r][punch_c]

        if not layers_at_punch_location:
             print(f"Warning: No paper layers found at the punch location ({punch_r},{punch_c}).")
             self.holes_unfolded = np.zeros((self.size, self.size), dtype=bool)
        else:
             print(f"\nUnfolding based on hole punched at ({punch_r},{punch_c}).")
             final_holes = np.zeros((self.size, self.size), dtype=bool)
             unique_orig_coords = set(layers_at_punch_location) # Use set for uniqueness
             print(f"Layers correspond to {len(unique_orig_coords)} unique original cells:")
             for orig_r, orig_c in unique_orig_coords:
                 print(f"  - Original cell: ({orig_r}, {orig_c})")
                 if 0 <= orig_r < self.size and 0 <= orig_c < self.size:
                     final_holes[orig_r, orig_c] = True
                 else:
                     print(f"   Warning: Original coordinate ({orig_r},{orig_c}) out of bounds.")
             self.holes_unfolded = final_holes
             print(f"Total unique unfolded holes: {np.sum(self.holes_unfolded)}")

        self._plot_unfolded()

    def run_simulation(self, num_folds=None):
        """Runs a full simulation with random folds and a random punch."""
        if num_folds is None:
            num_folds = random.randint(2, 3)
        print(f"--- Starting Simulation: {num_folds} random folds ---")

        folds_done = 0
        for i in range(num_folds):
            possible_folds = self.get_valid_folds()
            if not possible_folds:
                print(f"No more valid folds possible after {folds_done} folds.")
                break
            axis, line_coord = random.choice(possible_folds)
            if self.fold(axis, line_coord):
                 folds_done += 1
            else:
                 print("Warning: A chosen valid fold failed to execute. Stopping folds.")
                 break

        if folds_done == 0:
             print("Could not perform any folds.")
             # Plot final state even if no folds
             if not self.folds: self._plot_state("Final State (No Folds Performed)")
             return

        possible_punches = self.get_valid_punch_locations()
        if not possible_punches:
            print("Error: No valid locations left to punch a hole after folding.")
            self._plot_state(f"Final Folded State (No Punch Spot)") # Plot final folded state
            self.unfold() # Call unfold to plot the (empty) unfolded state
            return

        punch_r, punch_c = random.choice(possible_punches)
        if not self.punch_hole(punch_r, punch_c):
             print("Error: Failed to punch hole even at a chosen valid location.")
             return

        self.unfold()
        print(f"--- Simulation Complete --- Output saved in '{self.output_dir}' directory.")


# --- Run the Simulation ---
try:
    simulator = GridPaperSimulatorStyled(size=6, output_dir="folding_simulation_output")
    simulator.run_simulation(num_folds=3)

except ValueError as e:
    print(f"Initialization Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred during simulation: {e}")
    import traceback
    traceback.print_exc()