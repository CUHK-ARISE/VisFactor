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
        """初始化折纸模拟器"""
        self.grid_size = grid_size
        # 初始化纸张为正方形，用顶点坐标表示
        self.paper = ShapelyPolygon([
            (0, 0), (grid_size, 0),
            (grid_size, grid_size), (0, grid_size)
        ])
        self.fold_count = 0
        self.output_dir = "folding_results"
        self.fold_history = []  # 记录折叠历史

        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 保存初始状态
        self._draw_and_save()

    def fold(self, line_type, position):
        """
        沿指定线折叠纸张
        line_type: 'h'(水平), 'v'(垂直), 'd+'(斜率为+1的对角线), 'd-'(斜率为-1的对角线)
        position: 折叠线的位置
        返回: 是否成功执行了折叠
        """
        # 计算折叠线
        fold_line = self._get_fold_line(line_type, position)

        # 如果折叠线不与纸张相交，则不进行折叠
        if not fold_line.intersects(self.paper):
            print(f"折叠线不与纸张相交，跳过折叠")
            # 不增加fold_count，不记录历史，不输出PNG
            return False

        # 记录折叠历史
        self.fold_history.append((line_type, position))
        self.fold_count += 1

        # 将纸张分成两部分：保持不变的部分和需要折叠的部分
        line_coords = list(fold_line.coords)
        # 延长折叠线，确保它完全穿过纸张
        extended_line = self._extend_line(line_coords[0], line_coords[1])

        # 使用扩展的线分割纸张
        split_result = self._split_polygon_by_line(self.paper, extended_line)

        if len(split_result) != 2:
            print(f"折叠线没有正确分割纸张，跳过折叠 #{self.fold_count}")
            self._draw_and_save()
            return False

        # 确定哪一部分需要被折叠（通常是较小的那部分）
        part1, part2 = split_result
        if part1.area > part2.area:
            stationary_part, folding_part = part1, part2
        else:
            stationary_part, folding_part = part2, part1

        # 执行折叠（将folding_part沿fold_line反射）
        folded_part = self._reflect_polygon(folding_part, fold_line)

        # 合并两部分形成新的纸张
        self.paper = stationary_part.union(folded_part)

        # 绘制并保存结果
        self._draw_and_save()
        return True

    def _get_fold_line(self, line_type, position):
        """根据折叠类型和位置获取折叠线"""
        grid = self.grid_size

        if line_type == 'h':  # 水平线
            return LineString([(0, position), (grid, position)])

        elif line_type == 'v':  # 垂直线
            return LineString([(position, 0), (position, grid)])

        elif line_type == 'd+':  # 斜率为+1的对角线 (y = x + b)
            b = position
            # 找出与网格边界的交点
            intersections = []

            # 与左边界相交 (x=0)
            y_left = b
            if 0 <= y_left <= grid:
                intersections.append((0, y_left))

            # 与右边界相交 (x=grid)
            y_right = grid + b
            if 0 <= y_right <= grid:
                intersections.append((grid, y_right))

            # 与下边界相交 (y=0)
            x_bottom = -b
            if 0 <= x_bottom <= grid:
                intersections.append((x_bottom, 0))

            # 与上边界相交 (y=grid)
            x_top = grid - b
            if 0 <= x_top <= grid:
                intersections.append((x_top, grid))

            # 确保有两个交点
            if len(intersections) >= 2:
                return LineString([intersections[0], intersections[1]])
            else:
                return LineString([(0, 0), (0, 0)])  # 返回一个退化的线段

        elif line_type == 'd-':  # 斜率为-1的对角线 (y = -x + b)
            b = position
            # 找出与网格边界的交点
            intersections = []

            # 与左边界相交 (x=0)
            y_left = b
            if 0 <= y_left <= grid:
                intersections.append((0, y_left))

            # 与右边界相交 (x=grid)
            y_right = -grid + b
            if 0 <= y_right <= grid:
                intersections.append((grid, y_right))

            # 与下边界相交 (y=0)
            x_bottom = b
            if 0 <= x_bottom <= grid:
                intersections.append((x_bottom, 0))

            # 与上边界相交 (y=grid)
            x_top = b - grid
            if 0 <= x_top <= grid:
                intersections.append((x_top, grid))

            # 确保有两个交点
            if len(intersections) >= 2:
                return LineString([intersections[0], intersections[1]])
            else:
                return LineString([(0, 0), (0, 0)])  # 返回一个退化的线段

        else:
            raise ValueError("无效的折叠线类型")

    def _extend_line(self, p1, p2):
        """延长线段，确保它足够长以穿过整个纸张"""
        # 计算方向向量
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        # 避免除以零
        if dx == 0 and dy == 0:
            return LineString([p1, p2])

        # 计算延长因子（确保线足够长）
        extension_factor = 2 * self.grid_size / max(abs(dx), abs(dy)) if max(abs(dx), abs(dy)) > 0 else 1

        # 计算延长后的端点
        extended_p1 = (p1[0] - extension_factor * dx, p1[1] - extension_factor * dy)
        extended_p2 = (p2[0] + extension_factor * dx, p2[1] + extension_factor * dy)

        return LineString([extended_p1, extended_p2])

    def _split_polygon_by_line(self, polygon, line):
        """使用线分割多边形"""
        # 如果线不与多边形相交，则返回原多边形
        if not line.intersects(polygon):
            return [polygon]

        # 获取多边形的坐标
        poly_coords = list(polygon.exterior.coords)

        # 获取线的坐标
        line_coords = list(line.coords)

        # 计算线段方程 Ax + By + C = 0
        x1, y1 = line_coords[0]
        x2, y2 = line_coords[1]
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # 将点分为两组，基于它们相对于线的位置
        group1 = []
        group2 = []

        for point in poly_coords[:-1]:  # 排除最后一个点（它与第一个点重复）
            # 计算点到线的有符号距离
            x, y = point
            dist = (A * x + B * y + C) / np.sqrt(A ** 2 + B ** 2)

            if dist > 1e-10:  # 使用小的阈值来处理数值误差
                group1.append(point)
            elif dist < -1e-10:
                group2.append(point)
            else:  # 点在线上，添加到两个组
                group1.append(point)
                group2.append(point)

        # 计算线与多边形边界的交点
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

        # 去除重复的交点
        unique_intersections = []
        for point in intersections:
            if point not in unique_intersections:
                unique_intersections.append(point)

        # 如果有交点，将它们添加到两个组
        if len(unique_intersections) >= 2:
            for point in unique_intersections:
                if point not in group1:
                    group1.append(point)
                if point not in group2:
                    group2.append(point)

        # 创建两个新的多边形
        result = []
        if len(group1) >= 3:
            # 对点进行排序，使其形成有效的多边形
            group1 = self._sort_points_to_form_polygon(group1)
            poly1 = ShapelyPolygon(group1)
            if poly1.is_valid and poly1.area > 0:
                result.append(poly1)

        if len(group2) >= 3:
            # 对点进行排序，使其形成有效的多边形
            group2 = self._sort_points_to_form_polygon(group2)
            poly2 = ShapelyPolygon(group2)
            if poly2.is_valid and poly2.area > 0:
                result.append(poly2)

        return result

    def _sort_points_to_form_polygon(self, points):
        """将点排序，使其形成有效的多边形"""
        # 计算中心点
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)

        # 按照相对于中心点的角度排序
        def angle_to_center(point):
            return np.arctan2(point[1] - center_y, point[0] - center_x)

        sorted_points = sorted(points, key=angle_to_center)

        # 确保多边形闭合
        if sorted_points[0] != sorted_points[-1]:
            sorted_points.append(sorted_points[0])

        return sorted_points

    def _reflect_polygon(self, polygon, axis):
        """沿着给定的轴反射多边形"""
        # 获取轴的两个点
        axis_coords = list(axis.coords)
        p1, p2 = axis_coords[0], axis_coords[1]

        # 计算轴的方向向量
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        # 计算轴的角度（相对于x轴）
        angle = np.arctan2(dy, dx) * 180 / np.pi

        # 将多边形平移，使轴通过原点
        translated_polygon = translate(polygon, -p1[0], -p1[1])

        # 旋转多边形，使轴与x轴对齐
        rotated_polygon = rotate(translated_polygon, -angle, origin=(0, 0))

        # 沿x轴反射（即y坐标取反）
        reflected_coords = []
        for x, y in rotated_polygon.exterior.coords:
            reflected_coords.append((x, -y))

        reflected_polygon = ShapelyPolygon(reflected_coords)

        # 旋转回原来的角度
        rotated_back = rotate(reflected_polygon, angle, origin=(0, 0))

        # 平移回原来的位置
        final_polygon = translate(rotated_back, p1[0], p1[1])

        return final_polygon

    def _draw_and_save(self):
        """绘制当前纸张状态并保存为PNG"""
        fig, ax = plt.subplots(figsize=(8, 8))

        # 绘制网格
        for i in range(self.grid_size + 1):
            ax.axhline(y=i, color='gray', linestyle='-', alpha=0.3)
            ax.axvline(x=i, color='gray', linestyle='-', alpha=0.3)

        # 绘制纸张
        if self.paper.geom_type == 'Polygon':
            x, y = self.paper.exterior.xy
            ax.fill(x, y, alpha=0.7, fc='lightblue', ec='blue')
        elif self.paper.geom_type == 'MultiPolygon':
            for geom in self.paper.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, alpha=0.7, fc='lightblue', ec='blue')

        # 设置图形属性
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')
        ax.set_title(f'折叠 #{self.fold_count}')

        # 保存图像
        plt.savefig(os.path.join(self.output_dir, f'fold_{self.fold_count}.png'))
        plt.close()

    def random_fold(self, num_folds=5):
        """执行随机折叠，确保所有折叠线都严格沿着整数格线"""
        successful_folds = 0
        attempts = 0
        max_attempts = num_folds * 3  # 设置最大尝试次数，避免无限循环

        while successful_folds < num_folds and attempts < max_attempts:
            # 随机选择折叠线类型
            line_type = random.choice(['h', 'v', 'd+', 'd-'])

            # 随机选择折叠线位置（仅使用整数值）
            if line_type == 'h' or line_type == 'v':
                # 水平或垂直折叠线只能是整数（严格沿着格线）
                position = random.randint(0, self.grid_size)
            elif line_type == 'd+':
                # 对于y = x + b，确保b是整数
                position = random.randint(-self.grid_size, self.grid_size)
            else:  # line_type == 'd-'
                # 对于y = -x + b，确保b是整数
                position = random.randint(0, 2 * self.grid_size)

            # 尝试执行折叠
            if self.fold(line_type, position):
                successful_folds += 1

            attempts += 1

        return successful_folds

    def punch_hole(self):
        """在纸张上随机打一个孔，确保孔在格子的正中央"""
        # 确保纸张存在
        if self.paper.is_empty:
            print("纸张不存在，无法打孔")
            return None

        # 获取纸张的边界框
        minx, miny, maxx, maxy = self.paper.bounds

        # 创建所有可能的格子中心点
        possible_points = []
        for i in range(int(minx), int(maxx) + 1):
            for j in range(int(miny), int(maxy) + 1):
                # 格子中心点坐标
                center_x = i + 0.5
                center_y = j + 0.5

                # 检查点是否在纸张范围内
                if minx <= center_x <= maxx and miny <= center_y <= maxy:
                    possible_points.append((center_x, center_y))

        # 随机打乱可能的点
        random.shuffle(possible_points)

        # 尝试每个可能的点
        for x, y in possible_points:
            point = Point(x, y)

            # 检查点是否在纸张内
            if self.paper.contains(point):
                # 绘制并保存带孔的纸张
                self._draw_hole(point)
                return (x, y)

        print("无法在纸张上找到合适的打孔位置")
        return None

    def _draw_hole(self, point):
        """绘制带孔的纸张"""
        fig, ax = plt.subplots(figsize=(8, 8))

        # 绘制网格
        for i in range(self.grid_size + 1):
            ax.axhline(y=i, color='gray', linestyle='-', alpha=0.3)
            ax.axvline(x=i, color='gray', linestyle='-', alpha=0.3)

        # 绘制纸张
        if self.paper.geom_type == 'Polygon':
            x, y = self.paper.exterior.xy
            ax.fill(x, y, alpha=0.7, fc='lightblue', ec='blue')
        elif self.paper.geom_type == 'MultiPolygon':
            for geom in self.paper.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, alpha=0.7, fc='lightblue', ec='blue')

        # 绘制孔
        hole = Circle((point.x, point.y), 0.1, color='red')
        ax.add_patch(hole)

        # 设置图形属性
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')
        ax.set_title(f'带孔的折叠纸 #{self.fold_count}')

        # 保存图像
        plt.savefig(os.path.join(self.output_dir, f'fold_{self.fold_count}_with_hole.png'))
        plt.close()

    def unfold_and_show_holes(self, hole_coords):
        """展开纸张并显示所有孔的位置"""
        # 创建初始正方形纸张
        original_paper = ShapelyPolygon([
            (0, 0), (self.grid_size, 0),
            (self.grid_size, self.grid_size), (0, self.grid_size)
        ])

        # 将孔的坐标转换为点
        hole = Point(hole_coords)

        # 反向应用折叠历史，计算孔在原始纸张上的所有位置
        all_holes = [hole]
        current_paper = self.paper

        # 反向遍历折叠历史
        for line_type, position in reversed(self.fold_history):
            # 计算折叠线
            fold_line = self._get_fold_line(line_type, position)

            # 找出新的孔位置
            new_holes = []
            for h in all_holes:
                # 如果孔在折叠线一侧，添加其在另一侧的镜像
                if self._is_point_on_side(h, fold_line, current_paper):
                    mirrored_hole = self._mirror_point(h, fold_line)
                    new_holes.append(mirrored_hole)

            # 添加新发现的孔
            all_holes.extend(new_holes)

        # 过滤掉不在原始纸张上的孔
        valid_holes = [h for h in all_holes if original_paper.contains(h)]

        # 绘制原始纸张和所有孔
        fig, ax = plt.subplots(figsize=(8, 8))

        # 绘制网格
        for i in range(self.grid_size + 1):
            ax.axhline(y=i, color='gray', linestyle='-', alpha=0.3)
            ax.axvline(x=i, color='gray', linestyle='-', alpha=0.3)

        # 绘制原始纸张
        x, y = original_paper.exterior.xy
        ax.fill(x, y, alpha=0.5, fc='lightblue', ec='blue')

        # 绘制所有孔
        for h in valid_holes:
            hole = Circle((h.x, h.y), 0.1, color='red')
            ax.add_patch(hole)

        # 设置图形属性
        ax.set_xlim(-1, self.grid_size + 1)
        ax.set_ylim(-1, self.grid_size + 1)
        ax.set_aspect('equal')
        ax.set_title(f'展开图：{len(valid_holes)}个孔')

        # 保存图像
        plt.savefig(os.path.join(self.output_dir, 'unfolded_with_holes.png'))
        plt.close()

        return valid_holes

    def _is_point_on_side(self, point, line, reference_polygon):
        """
        判断点是否在折叠线的一侧（与参考多边形同侧）
        返回True表示点在参考多边形一侧，False表示点在折叠线上或另一侧
        """
        # 获取折叠线的两个点
        line_coords = list(line.coords)
        p1, p2 = line_coords[0], line_coords[1]

        # 计算折叠线的方程 Ax + By + C = 0
        A = p2[1] - p1[1]
        B = p1[0] - p2[0]
        C = p2[0] * p1[1] - p1[0] * p2[1]

        # 计算点到线的有符号距离
        dist = (A * point.x + B * point.y + C) / math.sqrt(A ** 2 + B ** 2)

        # 获取参考多边形上的一个点
        if reference_polygon.geom_type == 'Polygon':
            ref_point = Point(reference_polygon.exterior.coords[0])
        else:  # MultiPolygon
            ref_point = Point(reference_polygon.geoms[0].exterior.coords[0])

        # 计算参考点到线的有符号距离
        ref_dist = (A * ref_point.x + B * ref_point.y + C) / math.sqrt(A ** 2 + B ** 2)

        # 如果两个距离的符号相同，则点在参考多边形同侧
        return (dist * ref_dist > 0)

    def _mirror_point(self, point, axis):
        """沿着给定的轴镜像点"""
        # 获取轴的两个点
        axis_coords = list(axis.coords)
        p1, p2 = axis_coords[0], axis_coords[1]

        # 计算轴的方向向量
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        # 计算轴的角度（相对于x轴）
        angle = math.atan2(dy, dx) * 180 / math.pi

        # 将点平移，使轴通过原点
        translated_point = translate(point, -p1[0], -p1[1])

        # 旋转点，使轴与x轴对齐
        rotated_point = rotate(translated_point, -angle, origin=(0, 0))

        # 沿x轴镜像（即y坐标取反）
        mirrored_x = rotated_point.x
        mirrored_y = -rotated_point.y
        mirrored_point = Point(mirrored_x, mirrored_y)

        # 旋转回原来的角度
        rotated_back = rotate(mirrored_point, angle, origin=(0, 0))

        # 平移回原来的位置
        final_point = translate(rotated_back, p1[0], p1[1])

        return final_point


# 使用示例
if __name__ == "__main__":
    # 创建折纸模拟器
    folder = EnhancedPaperFolder(grid_size=6)

    # 执行随机折叠
    num_folds = random.randint(1,3)
    print(f"执行{num_folds}次随机折叠...")
    folder.random_fold(num_folds)

    # 打孔
    print("在纸张上随机打孔...")
    hole_coords = folder.punch_hole()

    if hole_coords:
        print(f"孔的坐标: {hole_coords}")

        # 展开并显示所有孔
        print("展开纸张并显示所有孔...")
        all_holes = folder.unfold_and_show_holes(hole_coords)
        print(f"展开后共有{len(all_holes)}个孔")
    else:
        print("打孔失败")
