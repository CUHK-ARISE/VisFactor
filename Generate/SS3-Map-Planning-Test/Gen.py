import matplotlib.pyplot as plt
import random
import string

def draw_grid_and_store_info(rows, cols, num_blocked_edges=20, num_buildings=10):
    fig, ax = plt.subplots(figsize=(cols, rows))
    point_info = {}

    # 初始化顶点信息
    for x in range(cols + 1):
        for y in range(rows + 1):
            point_info[(x, y)] = [
                1 if y < rows else 0,  # 上
                1 if y > 0 else 0,     # 下
                1 if x > 0 else 0,     # 左
                1 if x < cols else 0,  # 右
                [0, 0, 0, 0],          # 建筑信息[右上, 左上, 左下, 右下]
                ''                     # 字母标记（外围顶点）
            ]

    # 标记外围顶点（顺时针方向，从左上角开始）
    letters = list(string.ascii_uppercase)
    perimeter_points = []

    # 上边从左到右
    perimeter_points += [(x, rows) for x in range(cols + 1)]
    # 右边从上到下（不含第一个点）
    perimeter_points += [(cols, y) for y in range(rows - 1, -1, -1)]
    # 下边从右到左（不含第一个点）
    perimeter_points += [(x, 0) for x in range(cols - 1, -1, -1)]
    # 左边从下到上（不含第一个和最后一个点）
    perimeter_points += [(0, y) for y in range(1, rows)]

    # 字母标记稍微悬浮在外侧
    offset = 0.3
    for idx, (x, y) in enumerate(perimeter_points):
        letter = letters[idx % len(letters)]
        point_info[(x, y)][5] = letter

        # 根据位置确定字母偏移方向
        if y == rows:  # 上边
            ax.text(x, y + offset, letter, fontsize=14, color='black', ha='center', va='bottom', fontweight='bold')
        elif x == cols:  # 右边
            ax.text(x + offset, y, letter, fontsize=14, color='black', ha='left', va='center', fontweight='bold')
        elif y == 0:  # 下边
            ax.text(x, y - offset, letter, fontsize=14, color='black', ha='center', va='top', fontweight='bold')
        elif x == 0:  # 左边
            ax.text(x - offset, y, letter, fontsize=14, color='black', ha='right', va='center', fontweight='bold')

    # 所有可能的边
    edges = []
    for x in range(cols + 1):
        for y in range(rows + 1):
            if x < cols:
                edges.append(((x, y), (x + 1, y)))
            if y < rows:
                edges.append(((x, y), (x, y + 1)))

    # 随机阻塞边
    blocked_edges = random.sample(edges, min(num_blocked_edges, len(edges)))

    # 更新阻塞边信息
    for (start, end) in blocked_edges:
        x1, y1 = start
        x2, y2 = end
        if x1 == x2:  # 垂直边
            if y2 > y1:
                point_info[start][0] = 0
                point_info[end][1] = 0
            else:
                point_info[start][1] = 0
                point_info[end][0] = 0
        else:  # 水平边
            if x2 > x1:
                point_info[start][3] = 0
                point_info[end][2] = 0
            else:
                point_info[start][2] = 0
                point_info[end][3] = 0

    # 随机选择格子放置建筑
    all_cells = [(x, y) for x in range(cols) for y in range(rows)]
    building_cells = random.sample(all_cells, min(num_buildings, len(all_cells)))

    building_number = 1
    for (x, y) in building_cells:
        position = random.randint(1, 4)  # 1右上, 2左上, 3左下, 4右下
        half_size = 0.5
        if position == 1:  # 右上
            rect_x, rect_y = x + half_size, y + half_size
            point_info[(x + 1, y + 1)][4][2] = building_number
        elif position == 2:  # 左上
            rect_x, rect_y = x, y + half_size
            point_info[(x, y + 1)][4][3] = building_number
        elif position == 3:  # 左下
            rect_x, rect_y = x, y
            point_info[(x, y)][4][0] = building_number
        else:  # 右下
            rect_x, rect_y = x + half_size, y
            point_info[(x + 1, y)][4][1] = building_number

        building_rect = plt.Rectangle((rect_x, rect_y), half_size, half_size,
                                      facecolor='white', edgecolor='black')
        ax.add_patch(building_rect)

        ax.text(rect_x + half_size / 2, rect_y + half_size / 2, str(building_number),
                fontsize=12, ha='center', va='center')

        building_number += 1

    # 绘制网格线
    for x in range(cols + 1):
        ax.plot([x, x], [0, rows], color='black')
    for y in range(rows + 1):
        ax.plot([0, cols], [y, y], color='black')

    # 绘制阻塞边圆圈
    for (start, end) in blocked_edges:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.plot(mid_x, mid_y, 'o', markersize=12, markerfacecolor='white',
                markeredgecolor='black', markeredgewidth=1.5)

    ax.set_xlim(-1, cols + 1)
    ax.set_ylim(-1, rows + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.show()

    return point_info

# 调用函数并输出结果
rows, cols = 6, 7
grid_info = draw_grid_and_store_info(rows, cols, num_blocked_edges=15, num_buildings=10)
