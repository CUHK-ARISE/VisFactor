import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import split
import random

# 初始纸张
initial_square = Polygon([(0,0), (6,0), (6,6), (0,6)])

# 镜像翻转函数
def reflect_geom(geom, fold_line):
    p1, p2 = np.array(fold_line.coords[0]), np.array(fold_line.coords[1])
    fold_vec = p2 - p1
    reflected_coords = []
    for x, y in geom.coords:
        point = np.array([x,y])
        proj = p1 + np.dot(point - p1, fold_vec) / np.dot(fold_vec, fold_vec) * fold_vec
        reflect_point = 2 * proj - point
        reflected_coords.append(tuple(reflect_point))
    return type(geom)(reflected_coords)

# 绘图函数（考虑单面性，自动调整画布）
def plot_paper(layers, fold_lines, step):
    fig, ax = plt.subplots(figsize=(8,8))

    # 自动计算范围
    all_polygons = [layer['polygon'] for layer in layers] + [initial_square]
    minx, miny, maxx, maxy = all_polygons[0].bounds
    for poly in all_polygons[1:]:
        bx1, by1, bx2, by2 = poly.bounds
        minx, miny = min(minx, bx1), min(miny, by1)
        maxx, maxy = max(maxx, bx2), max(maxy, by2)
    margin = max(maxx - minx, maxy - miny) * 0.2
    ax.set_xlim(minx - margin, maxx + margin)
    ax.set_ylim(miny - margin, maxy + margin)
    ax.set_aspect('equal')
    ax.axis('off')

    # 原始纸张虚线边框
    x,y = initial_square.exterior.xy
    ax.plot(x,y,'--',color='gray', linewidth=2)

    # 绘制图层，正面浅蓝色，反面浅灰色
    for layer in layers:
        poly = layer['polygon']
        face_up = layer['face_up']
        x,y = poly.exterior.xy
        color = 'lightblue' if face_up else 'lightgray'
        ax.fill(x,y,facecolor=color,edgecolor='black',alpha=0.8)

    # 仅绘制位于最上层且正面可见的折痕
    top_layer = layers[-1]
    top_poly = top_layer['polygon']
    top_face_up = top_layer['face_up']

    for fold in fold_lines:
        fold_line = fold['line']
        fold_face_up = fold['face_up']
        if top_face_up != fold_face_up:
            continue  # 折痕凸起面与当前图层朝向不一致，不绘制

        # 计算折痕与最上层图层边界的交集
        intersection = fold_line.intersection(top_poly.boundary)

        # 仅当交集为线段（LineString或MultiLineString）时绘制
        if intersection.is_empty:
            continue
        if isinstance(intersection, (LineString, MultiLineString)):
            # 将单个LineString统一转成列表形式
            lines = [intersection] if isinstance(intersection, LineString) else intersection.geoms
            for line in lines:
                x, y = line.xy
                ax.plot(x, y, 'r-', linewidth=2)

    plt.title(f"Folding Step {step}")
    plt.show()

# 折叠函数（考虑图层正反面和折痕方向）
def fold_paper(layers, fold_line):
    new_layers = []
    flipped_layers = []

    p1, p2 = np.array(fold_line.coords[0]), np.array(fold_line.coords[1])
    fold_vec = p2 - p1
    normal = np.array([-fold_vec[1], fold_vec[0]])

    # 处理每个图层
    for layer in layers:
        poly, face_up = layer['polygon'], layer['face_up']
        splitted = split(poly, fold_line)
        for piece in splitted.geoms:
            centroid = np.array(piece.centroid.coords[0])
            if np.dot(centroid - p1, normal) >= 0:
                new_layers.append({'polygon': piece, 'face_up': face_up})
            else:
                flipped_piece = reflect_geom(piece.exterior, fold_line)
                flipped_layers.append({'polygon': Polygon(flipped_piece), 'face_up': not face_up})

    # 新图层顺序：未翻折部分在下，翻折部分在上
    layers_result = new_layers + flipped_layers

    # 新的折痕，凸起面为当前折叠方向的上方
    fold_face_up = True
    return layers_result, {'line': fold_line, 'face_up': fold_face_up}

# 随机生成折叠线
def random_fold_line():
    fold_type = random.choice(['horizontal', 'vertical', 'diagonal'])
    if fold_type == 'horizontal':
        y = random.randint(1,5)
        return LineString([(0,y),(6,y)])
    elif fold_type == 'vertical':
        x = random.randint(1,5)
        return LineString([(x,0),(x,6)])
    else:  # diagonal
        return random.choice([LineString([(0,0),(6,6)]), LineString([(0,6),(6,0)])])

# 主程序
def main():
    layers = [{'polygon': initial_square, 'face_up': True}]  # 初始正面朝上
    fold_lines = []
    fold_times = random.randint(2,3)

    for step in range(1, fold_times+1):
        fold_line = random_fold_line()
        layers, new_fold = fold_paper(layers, fold_line)
        fold_lines.append(new_fold)
        plot_paper(layers, fold_lines, step)

if __name__ == "__main__":
    main()
