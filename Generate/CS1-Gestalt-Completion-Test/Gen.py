import json
import os
import random
import numpy as np
from PIL import Image, ImageDraw
import glob
import datetime


def add_random_white_lines(input_folder, output_folder, num_lines_range=(10, 15), line_width_range=(30, 40)):
    """
    从输入文件夹读取所有PNG图片，在每张图片上随机添加白色线段以"擦除"部分内容，然后保存到输出文件夹

    参数:
    input_folder - 包含原始PNG图片的文件夹路径
    output_folder - 处理后图片的保存文件夹路径
    num_lines_range - 每张图片添加的线段数量范围，格式为(最小值, 最大值)
    line_width_range - 线段宽度范围，格式为(最小值, 最大值)
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

    print(f"\n开始处理图片，添加随机白色线段...")
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

            # 随机决定要添加的线段数量
            num_lines = random.randint(num_lines_range[0], num_lines_range[1])

            for _ in range(num_lines):
                # 随机线段起点和终点
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)

                # 随机线段宽度
                line_width = random.randint(line_width_range[0], line_width_range[1])

                # 绘制白色线段
                draw.line([(x1, y1), (x2, y2)], fill="white", width=line_width)

            # 保存修改后的图片到输出文件夹
            img.save(output_path)
            print(f"已添加白色线段并保存: {filename}")

        except Exception as e:
            print(f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    print(f"已完成所有图片的处理，共 {len(image_files)} 张图片")


# 设置输入和输出文件夹
input_folder = "Images"  # 原始图片所在文件夹
output_folder = "Quiz"  # 处理后图片的保存文件夹

# 调用函数处理图片
add_random_white_lines(input_folder, output_folder)
