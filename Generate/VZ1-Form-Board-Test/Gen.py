import math
import numpy as np
import matplotlib.pyplot as plt


def plot_region_centered(region, vertex_coords, filename):
    """
    根据 region 中顶点坐标，绘制该区域（多边形）使其居中显示，
    并将绘制结果保存到 filename 中。
    """
    coords = [vertex_coords[v] for v in region]
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
    绘制完整的多边形，并保存为图片。
    """
    coords = [vertex_coords[v] for v in polygon]
    coords.append(vertex_coords[polygon[0]])
    xs, ys = zip(*coords)
    plt.figure(figsize=(6, 6))
    plt.plot(xs, ys, marker='o')
    plt.fill(xs, ys, alpha=0.3)
    plt.gca().set_aspect('equal', 'box')
    plt.axis('off')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close()


def split_polygon(polygon, chord):
    """
    根据给定的 polygon（按顶点编号顺序排列）和连线 chord，
    切分多边形为两个区域。
    """
    a, b = chord
    try:
        idx_a = polygon.index(a)
        idx_b = polygon.index(b)
    except ValueError:
        return None

    if idx_a <= idx_b:
        segment1 = polygon[idx_a:idx_b + 1]
        segment2 = polygon[idx_b:] + polygon[:idx_a + 1]
    else:
        segment1 = polygon[idx_a:] + polygon[:idx_b + 1]
        segment2 = polygon[idx_b:idx_a + 1]
    return segment1, segment2


def main():
    # 1. 随机生成初始封闭多边形（保证点按角度排序）
    n = 8  # 可根据需要修改顶点数量
    angles = sorted(np.random.uniform(0, 2 * np.pi, n))
    # 随机半径，可控制多边形的扭曲程度
    radii = np.random.uniform(8, 12, n)

    # 按照排序后的顺序构造顶点字典：顶点编号 -> (x, y)
    vertex_coords = {}
    for i, (angle, r) in enumerate(zip(angles, radii), start=1):
        vertex_coords[i] = (r * math.cos(angle), r * math.sin(angle))

    # 初始多边形顶点顺序（按角度排序）
    initial_polygon = list(vertex_coords.keys())

    # 保存原始完整多边形图形
    plot_polygon(initial_polygon, vertex_coords, "original.png")

    # 2. 固定使用两条连线进行切分，保证最终切出 3 个区域
    # 这里仍使用预设的连线：(1, 5) 和 (5, 7)
    chords = [(1, 5), (5, 7)]
    regions = [initial_polygon]
    for chord in chords:
        new_regions = []
        for region in regions:
            if chord[0] in region and chord[1] in region:
                result = split_polygon(region, chord)
                if result:
                    seg1, seg2 = result
                    new_regions.extend([seg1, seg2])
                else:
                    new_regions.append(region)
            else:
                new_regions.append(region)
        regions = new_regions

    # 3. 仅保留切分出的 3 个区域，并对每个区域居中绘图后单独保存成图片
    if len(regions) == 3:
        for i, region in enumerate(regions, start=1):
            plot_region_centered(region, vertex_coords, f"region_{i}.png")


if __name__ == "__main__":
    main()
