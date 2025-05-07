import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque
import random
import math
import os

class GridPaperSimulatorFoldedEdges:
    """
    Simulates folding, punching, and unfolding of a grid-based paper.
    Visualizes internal grid lines, current boundaries, AND folded original boundaries.
    Outputs steps to PNG files.
    """
    def __init__(self, size=6, output_dir="folding_steps_edges"):
        if size <= 0 or not isinstance(size, int):
            raise ValueError("Size must be a positive integer.")
        self.size = size
        self.is_valid = np.ones((size, size), dtype=bool)
        self.paper_layers = [[deque([(r, c)]) for c in range(size)] for r in range(size)]
        self.folds = []
        self.hole_location_folded = None
        self.holes_unfolded = np.zeros((size, size), dtype=bool)
        self.output_dir = output_dir
        self.step_counter = 0
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")

        print(f"Initialized a {size}x{size} grid paper. Outputting steps to '{self.output_dir}/'")
        self._plot_state("Step 0: Initial Grid Paper")

    def get_current_bounds(self):
        rows, cols = np.where(self.is_valid)
        if len(rows) == 0: return None
        return rows.min(), rows.max(), cols.min(), cols.max()

    def _check_segment_is_folded_original(self, r, c, axis):
        """Checks if a line segment corresponds to an original boundary for any layer."""
        # Check horizontal segment at y=r, between x=c and x=c+1
        if axis == 'h':
            cell_above = (r - 1, c)
            cell_below = (r, c)
            # Check layers in cell_above for original top edge
            if 0 <= cell_above[0] < self.size and self.is_valid[cell_above]:
                for orig_r, _ in self.paper_layers[cell_above[0]][cell_above[1]]:
                    if orig_r == 0: return True
            # Check layers in cell_below for original bottom edge
            if 0 <= cell_below[0] < self.size and self.is_valid[cell_below]:
                for orig_r, _ in self.paper_layers[cell_below[0]][cell_below[1]]:
                    if orig_r == self.size - 1: return True
        # Check vertical segment at x=c, between y=r and y=r+1
        elif axis == 'v':
            cell_left = (r, c - 1)
            cell_right = (r, c)
            # Check layers in cell_left for original left edge
            if 0 <= cell_left[1] < self.size and self.is_valid[cell_left]:
                for _, orig_c in self.paper_layers[cell_left[0]][cell_left[1]]:
                    if orig_c == 0: return True
            # Check layers in cell_right for original right edge
            if 0 <= cell_right[1] < self.size and self.is_valid[cell_right]:
                 for _, orig_c in self.paper_layers[cell_right[0]][cell_right[1]]:
                     if orig_c == self.size - 1: return True
        return False


    def _plot_state(self, title):
        """Plots the current state with folded edge visualization and saves to PNG."""
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title(title, fontsize=12)
        self.step_counter += 1
        filename = os.path.join(self.output_dir, f"step_{self.step_counter:02d}_{title.replace(' ', '_').replace(':', '').replace('=', '').replace('(','').replace(')','')}.png")

        line_color_internal = 'lightgrey'
        line_color_boundary = 'black'
        line_width_internal = 0.5
        line_width_boundary = 1.5

        # --- Draw Grid Lines and Boundaries ---
        plotted_segments = set() # To avoid plotting segments twice

        for r in range(self.size + 1): # Horizontal lines Y = r
            for c in range(self.size): # Between X=c and X=c+1
                segment_id = (r, c, 'h')
                if segment_id in plotted_segments: continue

                is_above_valid = self.is_valid[r - 1, c] if 0 <= r - 1 < self.size else False
                is_below_valid = self.is_valid[r, c] if 0 <= r < self.size else False

                color = line_color_internal
                width = line_width_internal
                draw = False

                if is_above_valid != is_below_valid: # External Boundary
                    color = line_color_boundary
                    width = line_width_boundary
                    draw = True
                elif is_above_valid and is_below_valid: # Internal Line
                    if self._check_segment_is_folded_original(r, c, 'h'):
                        color = line_color_boundary # Folded Original Boundary
                        width = line_width_boundary
                    else:
                        color = line_color_internal # Internal Grid Line
                        width = line_width_internal
                    draw = True
                # else: both invalid, don't draw

                if draw:
                    ax.plot([c, c + 1], [r, r], color=color, lw=width, solid_capstyle='butt')
                    plotted_segments.add(segment_id)

        for c in range(self.size + 1): # Vertical lines X = c
            for r in range(self.size): # Between Y=r and Y=r+1
                segment_id = (r, c, 'v')
                if segment_id in plotted_segments: continue

                is_left_valid = self.is_valid[r, c - 1] if 0 <= c - 1 < self.size else False
                is_right_valid = self.is_valid[r, c] if 0 <= c < self.size else False

                color = line_color_internal
                width = line_width_internal
                draw = False

                if is_left_valid != is_right_valid: # External Boundary
                    color = line_color_boundary
                    width = line_width_boundary
                    draw = True
                elif is_left_valid and is_right_valid: # Internal Line
                    if self._check_segment_is_folded_original(r, c, 'v'):
                         color = line_color_boundary # Folded Original Boundary
                         width = line_width_boundary
                    else:
                         color = line_color_internal # Internal Grid Line
                         width = line_width_internal
                    draw = True
                # else: both invalid, don't draw

                if draw:
                    ax.plot([c, c], [r, r + 1], color=color, lw=width, solid_capstyle='butt')
                    plotted_segments.add(segment_id)


        # --- Draw Fold Lines (on top) ---
        fold_legend_added = False
        for axis, line_coord, _ in self.folds:
            label = 'Fold Line' if not fold_legend_added else '_nolegend_'
            if axis == 'h':
                 ax.plot([0, self.size], [line_coord, line_coord], 'r--', lw=1.5, label=label)
            else:
                 ax.plot([line_coord, line_coord], [0, self.size], 'r--', lw=1.5, label=label)
            fold_legend_added = True


        # --- Show Punched Hole Location ---
        if self.hole_location_folded:
            r_hole, c_hole = self.hole_location_folded
            ax.plot(c_hole + 0.5, r_hole + 0.5, 'ko', markersize=8, mfc='black', label=f'Punched at ({r_hole},{c_hole})')

        # --- Final Plot Setup ---
        ax.set_xlim(-0.5, self.size + 0.5)
        ax.set_ylim(-0.5, self.size + 0.5)
        ax.invert_yaxis()
        ax.set_aspect('equal', adjustable='box')
        plt.xlabel("Column Index")
        plt.ylabel("Row Index")
        plt.xticks(np.arange(self.size + 1))
        plt.yticks(np.arange(self.size + 1))
        plt.grid(False)
        # Add legend if folds or hole exist
        if self.folds or self.hole_location_folded:
             # Check if there are actual labels to display
             handles, labels = ax.get_legend_handles_labels()
             if labels:
                 ax.legend(fontsize=8, loc='best') # 'best' might be better than 'upper right'


        # --- Save and Close ---
        try:
            plt.savefig(filename)
            print(f"Saved state to {filename}")
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
        plt.close(fig)

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
            ax.plot(hole_cols + 0.5, hole_rows + 0.5, 'ro', markersize=8, mfc='red', label=f'{len(hole_rows)} Holes')
            ax.legend(fontsize=8)

        ax.set_xlim(-0.5, self.size + 0.5)
        ax.set_ylim(-0.5, self.size + 0.5)
        ax.invert_yaxis()
        ax.set_aspect('equal', adjustable='box')
        plt.xlabel("Column Index")
        plt.ylabel("Row Index")
        plt.xticks(np.arange(self.size + 1))
        plt.yticks(np.arange(self.size + 1))
        plt.grid(False)

        try:
            plt.savefig(filename)
            print(f"Saved final unfolded state to {filename}")
        except Exception as e:
            print(f"Error saving file {filename}: {e}")
        plt.close(fig)


    # --- Methods for folding, punching, unfolding (unchanged from previous version) ---
    def get_valid_folds(self):
        bounds = self.get_current_bounds()
        if bounds is None: return []
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
        bounds = self.get_current_bounds()
        if bounds is None: return False
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
        if not is_valid_choice: return False

        fold_away_indices, target_indices_func, folded_side_label = None, None, ""
        if axis == 'h':
            height_top = line_coord - min_r; height_bottom = (max_r + 1) - line_coord
            target_row_func = lambda r: 2 * line_coord - 1 - r
            if height_top <= height_bottom:
                fold_away_rows = range(min_r, line_coord); folded_side_label = "top"
            else:
                fold_away_rows = range(line_coord, max_r + 1); folded_side_label = "bottom"
            fold_away_indices = [(r, c) for r in fold_away_rows for c in range(min_c, max_c + 1)]
            target_indices_func = lambda r, c: (target_row_func(r), c)
        else: # axis == 'v'
            width_left = line_coord - min_c; width_right = (max_c + 1) - line_coord
            target_col_func = lambda c: 2 * line_coord - 1 - c
            if width_left <= width_right:
                fold_away_cols = range(min_c, line_coord); folded_side_label = "left"
            else:
                fold_away_cols = range(line_coord, max_c + 1); folded_side_label = "right"
            fold_away_indices = [(r, c) for r in range(min_r, max_r + 1) for c in fold_away_cols]
            target_indices_func = lambda r, c: (r, target_col_func(c))

        print(f"Performing Fold {len(self.folds) + 1}: axis={axis}, line={line_coord}, folding {folded_side_label} part.")
        for r_from, c_from in fold_away_indices:
            if self.is_valid[r_from, c_from]:
                r_to, c_to = target_indices_func(r_from, c_from)
                if 0 <= r_to < self.size and 0 <= c_to < self.size:
                     layers_to_move = self.paper_layers[r_from][c_from]
                     self.paper_layers[r_to][c_to].extend(layers_to_move)
                     self.paper_layers[r_from][c_from].clear()
                     self.is_valid[r_from, c_from] = False
                # else: Warning optional
        self.folds.append((axis, line_coord, folded_side_label))
        self._plot_state(f"After Fold {len(self.folds)} ({axis}={line_coord} fold {folded_side_label})")
        return True

    def get_valid_punch_locations(self):
        rows, cols = np.where(self.is_valid)
        return list(zip(rows, cols))

    def punch_hole(self, row, col):
        if not self.is_valid[row, col]: return False
        print(f"Punching hole at cell ({row}, {col}).")
        self.hole_location_folded = (row, col)
        self._plot_state("Paper with Hole Punched")
        return True

    def unfold(self):
        if self.hole_location_folded is None:
            print("No hole was punched. Nothing to unfold.")
            if self.folds: self._plot_state(f"Final Folded State (No Hole)")
            else: self._plot_state("Initial State (No Folds or Punch)")
            self._plot_unfolded() # Plot empty unfolded grid
            return

        punch_r, punch_c = self.hole_location_folded
        layers_at_punch_location = self.paper_layers[punch_r][punch_c]
        if not layers_at_punch_location:
             self.holes_unfolded = np.zeros((self.size, self.size), dtype=bool)
        else:
             print(f"\nUnfolding based on hole punched at ({punch_r},{punch_c}).")
             final_holes = np.zeros((self.size, self.size), dtype=bool)
             unique_orig_coords = set(layers_at_punch_location)
             print(f"Layers correspond to {len(unique_orig_coords)} unique original cells:")
             for orig_r, orig_c in unique_orig_coords:
                 print(f"  - Original cell: ({orig_r}, {orig_c})")
                 if 0 <= orig_r < self.size and 0 <= orig_c < self.size:
                     final_holes[orig_r, orig_c] = True
             self.holes_unfolded = final_holes
             print(f"Total unique unfolded holes: {np.sum(self.holes_unfolded)}")
        self._plot_unfolded()

    def run_simulation(self, num_folds=None):
        if num_folds is None: num_folds = random.randint(2, 3)
        print(f"--- Starting Simulation: {num_folds} random folds ---")
        folds_done = 0
        for i in range(num_folds):
            possible_folds = self.get_valid_folds()
            if not possible_folds: break
            axis, line_coord = random.choice(possible_folds)
            if self.fold(axis, line_coord): folds_done += 1
            else: break
        if folds_done == 0:
             if not self.folds: self._plot_state("Final State (No Folds Performed)")
             return
        possible_punches = self.get_valid_punch_locations()
        if not possible_punches:
            print("Error: No valid locations left to punch a hole after folding.")
            self._plot_state(f"Final Folded State (No Punch Spot)")
            self.unfold()
            return
        punch_r, punch_c = random.choice(possible_punches)
        if not self.punch_hole(punch_r, punch_c): return
        self.unfold()
        print(f"--- Simulation Complete --- Output saved in '{self.output_dir}' directory.")

# --- Run the Simulation ---
try:
    simulator = GridPaperSimulatorFoldedEdges(size=6, output_dir="folding_simulation_output_edges")
    # Example: Force the fold you described for testing
    print("\n--- Forcing Specific Fold for Testing ---")
    sim_test = GridPaperSimulatorFoldedEdges(size=6, output_dir="folding_test_fold_edge")
    # Fold bottom up along y=2 (line between row 1 and 2)
    sim_test.fold('h', 2) # This should show y=0 edge folded to y=3 (since target_row = 2*2-1-r = 3-r)
    # Now maybe fold right part left along x=4
    sim_test.fold('v', 4)
    # Punch a hole in a valid spot
    valid_spots = sim_test.get_valid_punch_locations()
    if valid_spots:
        r_punch, c_punch = valid_spots[0] # Punch first valid spot
        sim_test.punch_hole(r_punch, c_punch)
        sim_test.unfold()
    else:
        print("No valid spots to punch after forced folds.")
        sim_test._plot_state("Final State After Forced Folds (No Punch)")
        sim_test.unfold()

    # Run a random simulation as well
    # print("\n--- Running Random Simulation ---")
    # simulator_random = GridPaperSimulatorFoldedEdges(size=6, output_dir="folding_simulation_output_edges_random")
    # simulator_random.run_simulation(num_folds=3)


except ValueError as e:
    print(f"Initialization Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred during simulation: {e}")
    import traceback
    traceback.print_exc()
