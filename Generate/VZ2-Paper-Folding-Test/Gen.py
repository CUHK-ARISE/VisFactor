import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
import os
from datetime import datetime


class PaperFolding:
    def __init__(self, grid_size=6, img_size=600):
        self.grid_size = grid_size
        self.img_size = img_size
        self.cell_size = img_size // grid_size

        # Create the initial paper
        self.original_paper = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
        self.draw_grid(self.original_paper)

        # Track folding history
        self.folding_history = []
        self.current_paper = self.original_paper.copy()

        # Track transformations of each cell
        self.grid_mapping = np.zeros((grid_size, grid_size, 2), dtype=int)
        for i in range(grid_size):
            for j in range(grid_size):
                self.grid_mapping[i, j] = [i, j]

        # Save images of all steps
        self.step_images = [self.original_paper.copy()]
        self.step_titles = ["Original Paper"]

    def draw_grid(self, img):
        """Draw grid lines on the image."""
        for i in range(self.grid_size + 1):
            # Horizontal line
            cv2.line(img, (0, i * self.cell_size),
                     (self.img_size, i * self.cell_size),
                     (150, 150, 150), 2)
            # Vertical line
            cv2.line(img, (i * self.cell_size, 0),
                     (i * self.cell_size, self.img_size),
                     (150, 150, 150), 2)

        # Add grid coordinate labels
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cv2.putText(img, f"({i},{j})",
                            (j * self.cell_size + 10, i * self.cell_size + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)

    def fold_horizontal(self, fold_line):
        """Horizontal fold (top part to bottom part)."""
        if fold_line <= 0 or fold_line >= self.grid_size:
            print("Invalid fold line position.")
            return False

        # Record folding history
        self.folding_history.append(("horizontal", fold_line))

        # Calculate pixel position of the fold line
        fold_pixel = fold_line * self.cell_size

        # Create a new paper image
        new_height = max(fold_pixel, self.current_paper.shape[0] - fold_pixel)
        folded_paper = np.ones((new_height, self.current_paper.shape[1], 3), dtype=np.uint8) * 255

        # Copy the top part
        top_part = self.current_paper[:fold_pixel, :]
        folded_paper[:fold_pixel, :] = top_part

        # Flip and copy the bottom part
        bottom_part = self.current_paper[fold_pixel:, :]
        flipped_bottom = cv2.flip(bottom_part, 0)  # Flip vertically

        # If the bottom part is smaller than the top part, only copy the overlapping part
        overlap_height = min(fold_pixel, flipped_bottom.shape[0])

        # Display a translucent effect in the overlapping area
        folded_paper[:overlap_height, :] = cv2.addWeighted(
            folded_paper[:overlap_height, :], 0.5,
            flipped_bottom[:overlap_height, :], 0.5, 0
        )

        # Update grid mapping
        new_mapping = self.grid_mapping.copy()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if i >= fold_line:  # Bottom part is folded
                    new_i = 2 * fold_line - i - 1
                    if 0 <= new_i < self.grid_size:
                        new_mapping[new_i, j] = self.grid_mapping[i, j]

        self.grid_mapping = new_mapping
        self.current_paper = folded_paper

        # Save this step's image
        img_with_text = folded_paper.copy()
        cv2.putText(img_with_text, f"Horizontal Fold (Fold Line={fold_line})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.step_images.append(img_with_text)
        self.step_titles.append(f"Horizontal Fold (Fold Line={fold_line})")
        return True

    def fold_vertical(self, fold_line):
        """Vertical fold (left part to right part)."""
        if fold_line <= 0 or fold_line >= self.grid_size:
            print("Invalid fold line position.")
            return False

        # Record folding history
        self.folding_history.append(("vertical", fold_line))

        # Calculate pixel position of the fold line
        fold_pixel = fold_line * self.cell_size

        # Create a new paper image
        new_width = max(fold_pixel, self.current_paper.shape[1] - fold_pixel)
        folded_paper = np.ones((self.current_paper.shape[0], new_width, 3), dtype=np.uint8) * 255

        # Copy the left part
        left_part = self.current_paper[:, :fold_pixel]
        folded_paper[:, :fold_pixel] = left_part

        # Flip and copy the right part
        right_part = self.current_paper[:, fold_pixel:]
        flipped_right = cv2.flip(right_part, 1)  # Flip horizontally

        # If the right part is smaller than the left part, only copy the overlapping part
        overlap_width = min(fold_pixel, flipped_right.shape[1])

        # Display a translucent effect in the overlapping area
        folded_paper[:, :overlap_width] = cv2.addWeighted(
            folded_paper[:, :overlap_width], 0.5,
            flipped_right[:, :overlap_width], 0.5, 0
        )

        # Update grid mapping
        new_mapping = self.grid_mapping.copy()
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if j >= fold_line:  # Right part is folded
                    new_j = 2 * fold_line - j - 1
                    if 0 <= new_j < self.grid_size:
                        new_mapping[i, new_j] = self.grid_mapping[i, j]

        self.grid_mapping = new_mapping
        self.current_paper = folded_paper

        # Save this step's image
        img_with_text = folded_paper.copy()
        cv2.putText(img_with_text, f"Vertical Fold (Fold Line={fold_line})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.step_images.append(img_with_text)
        self.step_titles.append(f"Vertical Fold (Fold Line={fold_line})")
        return True

    def fold_diagonal(self, random_edge=True, edge=None, position=None):
        """
        实现斜向45°折叠。

        参数:
            random_edge: 是否随机选择边
            edge: 指定边 ('top', 'bottom', 'left', 'right')
            position: 在边上的位置比例 (0.0-1.0)

        返回:
            成功折叠返回True，否则False
        """
        # 如果需要随机选择边和位置
        if random_edge or edge is None or position is None:
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            position = random.random()  # 0.0 到 1.0 之间的随机数

        # 计算边上的点坐标
        if edge == 'top':
            start_x = int(position * self.img_size)
            start_y = 0
            # 45°向下折叠，计算终点
            if start_x <= self.img_size / 2:
                # 折线会碰到左边界
                end_x = 0
                end_y = start_y + start_x
            else:
                # 折线会碰到底边界
                end_x = start_x - (self.img_size - start_y)
                end_y = self.img_size

        elif edge == 'bottom':
            start_x = int(position * self.img_size)
            start_y = self.img_size
            # 45°向上折叠，计算终点
            if start_x <= self.img_size / 2:
                # 折线会碰到左边界
                end_x = 0
                end_y = start_y - start_x
            else:
                # 折线会碰到顶边界
                end_x = start_x - start_y
                end_y = 0

        elif edge == 'left':
            start_x = 0
            start_y = int(position * self.img_size)
            # 45°向右折叠，计算终点
            if start_y <= self.img_size / 2:
                # 折线会碰到顶边界
                end_x = start_x + start_y
                end_y = 0
            else:
                # 折线会碰到右边界
                end_x = self.img_size
                end_y = start_y - (self.img_size - start_x)

        elif edge == 'right':
            start_x = self.img_size
            start_y = int(position * self.img_size)
            # 45°向左折叠，计算终点
            if start_y <= self.img_size / 2:
                # 折线会碰到顶边界
                end_x = start_x - start_y
                end_y = 0
            else:
                # 折线会碰到左边界
                end_x = 0
                end_y = start_y - start_x

        else:
            return False  # 无效的边

        # 记录折叠历史
        self.folding_history.append(("diagonal", (edge, position)))

        # 创建折叠后的纸张图像
        folded_paper = self.current_paper.copy ()

        # 绘制折叠线（用于可视化）
        cv2.line(folded_paper, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)

        # 计算折叠变换矩阵
        # 这里需要计算将折叠部分映射到另一侧的仿射变换
        # 首先找出折叠线两侧的区域

        # 创建掩码来确定哪部分被折叠
        mask = np.zeros((self.img_size, self.img_size), dtype=np.uint8)

        # 绘制折叠线和边界形成的多边形区域（这是要被折叠的部分）
        if edge == 'top':
            pts = np.array([[0, 0], [start_x, start_y], [end_x, end_y], [0, end_y]], dtype=np.int32)
            if start_x > self.img_size / 2:
                pts = np.array([[start_x, start_y], [self.img_size, 0], [self.img_size, end_y], [end_x, end_y]],
                               dtype=np.int32)
        elif edge == 'bottom':
            pts = np.array([[0, self.img_size], [start_x, start_y], [end_x, end_y], [0, end_y]], dtype=np.int32)
            if start_x > self.img_size / 2:
                pts = np.array(
                    [[start_x, start_y], [self.img_size, self.img_size], [self.img_size, end_y], [end_x, end_y]],
                    dtype=np.int32)
        elif edge == 'left':
            pts = np.array([[0, 0], [start_x, start_y], [end_x, end_y], [end_x, 0]], dtype=np.int32)
            if start_y > self.img_size / 2:
                pts = np.array([[0, start_y], [start_x, start_y], [end_x, end_y], [0, self.img_size]], dtype=np.int32)
        elif edge == 'right':
            pts = np.array([[self.img_size, 0], [start_x, start_y], [end_x, end_y], [end_x, 0]], dtype=np.int32)
            if start_y > self.img_size / 2:
                pts = np.array(
                    [[self.img_size, start_y], [start_x, start_y], [end_x, end_y], [self.img_size, self.img_size]],
                    dtype=np.int32)

        # 填充多边形区域
        cv2.fillPoly(mask, [pts], 255)

        # 计算折叠线的中点
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        # 计算折叠线的方向向量
        dx = end_x - start_x
        dy = end_y - start_y

        # 归一化方向向量
        length = np.sqrt(dx * dx + dy * dy)
        dx /= length
        dy /= length

        # 计算垂直于折叠线的向量
        nx = -dy
        ny = dx

        # 对于掩码中的每个点，计算它在折叠后的新位置
        for i in range(self.img_size):
            for j in range(self.img_size):
                if mask[j, i] > 0:  # 如果这个点在被折叠区域内
                    # 计算点到折叠线的距离
                    # 使用点到直线的距离公式
                    dist = abs(
                        (end_y - start_y) * i - (end_x - start_x) * j + end_x * start_y - end_y * start_x) / length

                    # 计算沿折叠线的投影位置
                    t = ((i - start_x) * dx + (j - start_y) * dy) / length

                    # 计算折叠线上的投影点
                    proj_x = start_x + t * dx
                    proj_y = start_y + t * dy

                    # 计算反射点
                    refl_x = int(2 * proj_x - i)
                    refl_y = int(2 * proj_y - j)

                    # 确保反射点在图像范围内
                    if 0 <= refl_x < self.img_size and 0 <= refl_y < self.img_size:
                        # 更新网格映射
                        grid_i = j // self.cell_size
                        grid_j = i // self.cell_size
                        refl_grid_i = refl_y // self.cell_size
                        refl_grid_j = refl_x // self.cell_size

                        if (grid_i, grid_j) in self.grid_mapping and (refl_grid_i, refl_grid_j) in self.grid_mapping:
                            self.grid_mapping[(refl_grid_i, refl_grid_j)].extend(self.grid_mapping[(grid_i, grid_j)])
                            self.grid_mapping.pop((grid_i, grid_j), None)

        # 保存这一步的图像
        img_with_text = folded_paper.copy()
        cv2.putText(img_with_text, f"Diagnal fols (edge={edge}, position={position:.2f})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.step_images.append(img_with_text)
        self.step_titles.append(f"对角折叠 (边={edge}, 位置={position:.2f})")

        return True

    def punch_holes(self, num_holes=1):
        """Randomly punch holes in the current folded paper."""
        # Copy the current paper
        punched_paper = self.current_paper.copy()

        # Get the dimensions of the current paper
        current_height, current_width = punched_paper.shape[:2]

        # Calculate the number of visible cells
        visible_rows = current_height // self.cell_size
        visible_cols = current_width // self.cell_size

        # Record original hole positions
        self.hole_positions = []

        # Randomly select positions to punch holes
        hole_positions = []
        for _ in range(num_holes):
            row = random.randint(0, visible_rows - 1)
            col = random.randint(0, visible_cols - 1)
            hole_positions.append((row, col))

        # Punch holes at specified positions
        for pos in hole_positions:
            row, col = pos
            # Calculate the center pixel position of the hole
            center_y = int((row + 0.5) * self.cell_size)
            center_x = int((col + 0.5) * self.cell_size)

            # Ensure the position is within the bounds of the current paper
            if (0 <= center_y < punched_paper.shape[0] and
                    0 <= center_x < punched_paper.shape[1]):
                # Draw a black circle to represent the hole
                cv2.circle(punched_paper, (center_x, center_y),
                           self.cell_size // 4, (0, 0, 0), -1)

                # Record original hole positions
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        if list(self.grid_mapping[i, j]) == [row, col]:
                            self.hole_positions.append((i, j))

        self.current_paper = punched_paper

        # Save this step's image
        img_with_text = punched_paper.copy()
        cv2.putText(img_with_text, f"Random Punching ({len(hole_positions)} holes)",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.step_images.append(img_with_text)
        self.step_titles.append(f"Random Punching ({len(hole_positions)} holes)")

    def unfold(self):
        """Unfold the paper, displaying all hole positions."""
        # Create a new white paper
        unfolded_paper = self.original_paper.copy()

        # Mark all holes at their original positions
        for pos in self.hole_positions:
            row, col = pos
            # Calculate the center pixel position of the hole
            center_y = int((row + 0.5) * self.cell_size)
            center_x = int((col + 0.5) * self.cell_size)

            # Draw a black circle to represent the hole
            cv2.circle(unfolded_paper, (center_x, center_y),
                       self.cell_size // 4, (0, 0, 0), -1)

        # Save the unfolded image
        img_with_text = unfolded_paper.copy()
        cv2.putText(img_with_text, "Unfolded Paper",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        self.step_images.append(img_with_text)
        self.step_titles.append("Unfolded Paper")

        return unfolded_paper

    def save_all_steps(self, output_dir="paper_folding_results"):
        """Save all step images to files."""
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate a unique timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save each step's image
        for i, (img, title) in enumerate(zip(self.step_images, self.step_titles)):
            filename = f"{output_dir}/step_{i:02d}_{title.replace(' ', '_')}_{timestamp}.png"
            cv2.imwrite(filename, img)
            print(f"Saved: {filename}")

        # Create a combined image of all steps
        plt.figure(figsize=(15, 5 * ((len(self.step_images) + 2) // 3)))
        for i, (img, title) in enumerate(zip(self.step_images, self.step_titles)):
            plt.subplot(((len(self.step_images) + 2) // 3), 3, i + 1)
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.title(title)
            plt.axis('off')

        # Save the combined image
        combined_filename = f"{output_dir}/combined_steps_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(combined_filename)
        print(f"Saved combined image: {combined_filename}")
        plt.close()

    def display_all_steps(self):
        """Display all step images."""
        plt.figure(figsize=(15, 5 * ((len(self.step_images) + 2) // 3)))
        for i, (img, title) in enumerate(zip(self.step_images, self.step_titles)):
            plt.subplot(((len(self.step_images) + 2) // 3), 3, i + 1)
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.title(title)
            plt.axis('off')
        plt.tight_layout()
        plt.show()


# Main program
def run_paper_folding_simulation(num_folds=3, num_holes=1):
    """Run paper folding simulation."""
    paper = PaperFolding(grid_size=6, img_size=600)

    # Randomly perform several folds
    fold_types = ["horizontal", "vertical", "diagonal"]

    for _ in range(num_folds):
        fold_type = random.choice(fold_types)

        if fold_type == "horizontal":
            fold_line = random.randint(1, paper.grid_size - 1)
            paper.fold_horizontal(fold_line)

        elif fold_type == "vertical":
            fold_line = random.randint(1, paper.grid_size - 1)
            paper.fold_vertical(fold_line)

        elif fold_type == "diagonal":
            # 使用新的对角线折叠函数，随机选择边和位置
            paper.fold_diagonal()  # 默认参数 random_edge=True 会随机选择边和位置

    # Punch holes
    paper.punch_holes(num_holes)

    # Unfold
    paper.unfold()

    # Save all steps
    paper.save_all_steps()

    # Display all steps
    paper.display_all_steps()

    return paper



if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(100)

    # Run the simulation
    paper = run_paper_folding_simulation(num_folds=3, num_holes=2)