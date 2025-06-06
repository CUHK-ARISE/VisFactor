import os
import glob
import random
import numpy as np
from PIL import Image, ImageDraw

def add_noise_lines(input_folder, output_folder, num_lines_range=(3000, 4000), line_length=5, line_width_range=(5, 8)):
    """
    从输入文件夹读取所有PNG图片，在每张图片上添加密集的黑色小短细线作为噪声，然后保存到输出文件夹

    参数:
    input_folder - 包含原始PNG图片的文件夹路径
    output_folder - 处理后图片的保存文件夹路径
    num_lines_range - 每张图片添加的噪声线条数量范围，格式为(最小值, 最大值)
    line_length - 噪声线条的固定长度
    line_width_range - 噪声线条宽度范围，格式为(最小值, 最大值)
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")

    # 获取输入文件夹中的所有PNG图片
    image_files = glob.glob(os.path.join(input_folder, "*.png"))

    if not image_files:
        print(f"错误：在 {input_folder} 中没有找到PNG图片")
        return

    print(f"\n开始处理图片，添加黑色噪声线条...")
    print(f"从 {input_folder} 读取图片，处理后保存到 {output_folder}")

    for image_path in image_files:
        try:
            # 获取文件名（不含路径）
            filename = os.path.basename(image_path)
            # 构建输出路径
            output_path = os.path.join(output_folder, filename)

            # 打开图片
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)

            # 获取图片尺寸
            width, height = img.size

            # 随机决定要添加的噪声线条数量
            num_lines = random.randint(num_lines_range[0], num_lines_range[1])

            for _ in range(num_lines):
                # 随机选择起点
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)

                # 使用固定线条长度，但随机角度
                angle = random.uniform(0, 2 * 3.14159)  # 随机角度（弧度）

                # 计算终点坐标
                x2 = int(x1 + line_length * np.cos(angle))
                y2 = int(y1 + line_length * np.sin(angle))

                # 确保终点在图像范围内
                x2 = max(0, min(width, x2))
                y2 = max(0, min(height, y2))

                # 随机线条宽度
                line_width = random.randint(line_width_range[0], line_width_range[1])

                # 绘制黑色噪声线条
                draw.line([(x1, y1), (x2, y2)], fill="black", width=line_width)

            # 保存修改后的图片到输出文件夹
            img.save(output_path)
            print(f"已添加噪声并保存: {filename}")

        except Exception as e:
            print(f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    print(f"已完成所有图片的噪声处理，共 {len(image_files)} 张图片")

# 设置输入和输出文件夹
input_folder = "Images"  # 原始图片所在文件夹
output_folder = "quiz_images"  # 处理后图片的保存文件夹

# 调用函数处理图片
add_noise_lines(input_folder, output_folder, line_length=13)  # 使用固定长度为5的线条

