import json
import os
import random
import numpy as np
from PIL import Image, ImageDraw
import glob
import datetime
def add_random_white_lines(image_folder, num_lines_range=(10, 15), line_width_range=(40, 50)):
    """
    遍历文件夹中的所有PNG图片，在每张图片上随机添加白色线段以"擦除"部分内容

    参数:
    image_folder - 包含PNG图片的文件夹路径
    num_lines_range - 每张图片添加的线段数量范围，格式为(最小值, 最大值)
    line_width_range - 线段宽度范围，格式为(最小值, 最大值)
    """
    # 获取文件夹中的所有PNG图片
    image_files = glob.glob(os.path.join(image_folder, "*.png"))

    if not image_files:
        print(f"错误：在 {image_folder} 中没有找到PNG图片")
        return

    print(f"\n开始处理图片，添加随机白色线段...")

    for image_path in image_files:
        try:
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

            # 保存修改后的图片
            img.save(image_path)
            print(f"已处理: {os.path.basename(image_path)}")

        except Exception as e:
            print(f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    print(f"已完成所有图片的处理，共 {len(image_files)} 张图片")

# 调用函数处理quiz_images文件夹中的图片
output_folder = "Images"  # 您的图片输出文件夹
add_random_white_lines(output_folder)
