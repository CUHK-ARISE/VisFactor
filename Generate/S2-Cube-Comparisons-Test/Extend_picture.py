from PIL import Image
import os
import json
import glob
import random
import cv2
import sys

# 导入Gen.py中的相关类和函数
sys.path.append('.')
from Gen import CubeQuestionGenerator
from DrawCube import draw_cube

# 定义旋转和翻转的操作
transformations = [
    ("rotate_90", lambda img: img.rotate(90)),
    ("rotate_180", lambda img: img.rotate(180)),
    ("rotate_270", lambda img: img.rotate(270)),
    ("flip_horizontal", lambda img: img.transpose(Image.FLIP_LEFT_RIGHT)),
]

# 确保目标文件夹存在
output_folder = "Images"
os.makedirs(output_folder, exist_ok=True)

# 初始化立方体生成器（用于生成第6组）
cube_generator = CubeQuestionGenerator()

# 动态检测有多少对图片
def count_image_pairs():
    # 在Images文件夹中查找图片
    pattern_0 = os.path.join("Images", "*-0.jpg")
    pattern_1 = os.path.join("Images", "*-1.jpg")
    
    files_0 = glob.glob(pattern_0)
    files_1 = glob.glob(pattern_1)
    
    print(f"Found {len(files_0)} files with -0.jpg pattern")
    print(f"Found {len(files_1)} files with -1.jpg pattern")
    
    # 提取图片编号
    numbers_0 = set()
    numbers_1 = set()
    
    for file in files_0:
        # 从 "Images/n-0.jpg" 中提取 n
        filename = os.path.basename(file)
        num = int(filename.split('-')[0])
        numbers_0.add(num)
    
    for file in files_1:
        # 从 "Images/n-1.jpg" 中提取 n
        filename = os.path.basename(file)
        num = int(filename.split('-')[0])
        numbers_1.add(num)
    
    # 找到同时有-0和-1的图片编号
    common_numbers = numbers_0.intersection(numbers_1)
    return sorted(list(common_numbers))

def load_question_data(question_num):
    """加载指定问题的详细数据"""
    data_file = os.path.join("Images", f"question_{question_num}_data.json")
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_same_cube_view_for_d_to_s(cube_data):
    """为D->S生成相同立方体的新视角（same_3_faces方法）"""
    # 确保立方体数据的键是整数格式
    normalized_cube_data = {}
    for key, value in cube_data.items():
        # 将键转换为整数
        int_key = int(key) if isinstance(key, str) else key
        normalized_cube_data[int_key] = value
    
    # 使用same_3_faces的方法找到显示相同3个面的新配置
    config_1, config_2, visible_1, visible_2 = cube_generator.find_configs_with_same_faces(normalized_cube_data, 3)
    
    # 如果找不到3个相同面，尝试2个相同面
    if cube_generator.count_same_faces(visible_1, visible_2) < 2:
        config_1, config_2, visible_1, visible_2 = cube_generator.find_configs_with_same_faces(normalized_cube_data, 2)
    
    return config_2, visible_2

def generate_modified_cube_for_s_to_d(original_cube_data, visible_faces_data):
    """为S->D生成修改后的立方体（修改一个可见面的内容为#）"""
    # 确保立方体数据的键是整数格式
    modified_cube = {}
    for key, value in original_cube_data.items():
        int_key = int(key) if isinstance(key, str) else key
        modified_cube[int_key] = value.copy() if isinstance(value, dict) else value
    
    # 获取可见面编号
    visible_face_nums = [
        visible_faces_data['front']['face_num'],
        visible_faces_data['up']['face_num'],
        visible_faces_data['right']['face_num']
    ]
    
    # 随机选择一个可见面进行修改
    face_to_modify = random.choice(visible_face_nums)
    
    # 统一替换为#符号
    original_content = modified_cube[face_to_modify]['content']
    modified_cube[face_to_modify]['content'] = '#'
    modified_cube[face_to_modify]['rotation'] = 0  # #符号不需要旋转
    
    print(f"Modified face {face_to_modify}: {original_content} -> #")
    
    return modified_cube

def generate_cube_image_from_data(visible_faces, filename):
    """根据可见面数据生成立方体图片"""
    cube_img = draw_cube(
        up_text=visible_faces['up']['content'],
        front_text=visible_faces['front']['content'],
        right_text=visible_faces['right']['content'],
        up_rot=visible_faces['up']['rotation'],
        front_rot=visible_faces['front']['rotation'],
        right_rot=visible_faces['right']['rotation'],
        size=300,
        offset_ratio=0.35,
        text_color=(0, 0, 0),
        font_scale=7
    )
    
    filepath = os.path.join(output_folder, filename)
    cv2.imwrite(filepath, cube_img)
    print(f"Generated: {filename}")

# 获取图片对列表
image_pairs = count_image_pairs()
print(f"Found {len(image_pairs)} image pairs: {image_pairs}")

if len(image_pairs) == 0:
    print("No image pairs found. Please check if Images folder contains the original images.")
    print("Expected format: Images/1-0.jpg, Images/1-1.jpg, etc.")
    exit()

# 处理每对图片 - 生成4个变换版本
for n in image_pairs:
    # 处理 -0.jpg 和 -1.jpg
    for suffix in [0, 1]:
        img_path = os.path.join("Images", f"{n}-{suffix}.jpg")
        if os.path.exists(img_path):
            img = Image.open(img_path)
            
            for i, (name, transform) in enumerate(transformations):
                new_img = transform(img)
                new_filename = f"{n + (i + 1) * len(image_pairs)}-{suffix}.jpg"
                new_img.save(os.path.join(output_folder, new_filename))
                print(f"Generated: {new_filename} from {os.path.basename(img_path)} using {name}")

# 生成第6组图片
print("\nGenerating 6th group with opposite answers...")
for idx, n in enumerate(image_pairs):
    # 加载原始问题数据
    question_data = load_question_data(n)
    if not question_data:
        print(f"Warning: Could not load data for question {n}, skipping 6th group generation")
        continue
    
    # 确定第6组的编号
    sixth_group_n = n + 5 * len(image_pairs)
    
    # 根据原始答案生成相反的答案
    original_answer = question_data.get('question_type', 'Same')
    
    if 'Same' in original_answer:
        # 原始是S，第6组生成D
        print(f"Converting S to D for question {n} -> {sixth_group_n}")
        
        # 复制原始的-0.jpg
        original_0_path = os.path.join("Images", f"{n}-0.jpg")
        new_0_path = os.path.join("Images", f"{sixth_group_n}-0.jpg")
        if os.path.exists(original_0_path):
            img = Image.open(original_0_path)
            img.save(new_0_path)
            print(f"Copied: {n}-0.jpg -> {sixth_group_n}-0.jpg")
        
        # 生成修改后的立方体作为-1.jpg
        original_cube = question_data['cube_faces']
        original_visible = question_data['view_2']['visible_faces']
        
        modified_cube = generate_modified_cube_for_s_to_d(original_cube, original_visible)
        modified_visible = cube_generator.get_visible_faces(
            modified_cube, 
            question_data['view_2']['config'][0], 
            question_data['view_2']['config'][1]
        )
        
        generate_cube_image_from_data(modified_visible, f"{sixth_group_n}-1.jpg")
        
    else:
        # 原始是D，第6组生成S
        print(f"Converting D to S for question {n} -> {sixth_group_n}")
        
        # 复制原始的-0.jpg
        original_0_path = os.path.join("Images", f"{n}-0.jpg")
        new_0_path = os.path.join("Images", f"{sixth_group_n}-0.jpg")
        if os.path.exists(original_0_path):
            img = Image.open(original_0_path)
            img.save(new_0_path)
            print(f"Copied: {n}-0.jpg -> {sixth_group_n}-0.jpg")
        
        # 使用第一个立方体生成相同立方体的新视角
        cube_1 = question_data['cube_faces_1']
        
        try:
            new_config, new_visible = generate_same_cube_view_for_d_to_s(cube_1)
            generate_cube_image_from_data(new_visible, f"{sixth_group_n}-1.jpg")
        except Exception as e:
            print(f"Error generating same cube view for question {n}: {e}")
            print("Using fallback method - copying original image")
            # 作为备选方案，直接复制原始图片并稍作修改
            original_1_path = os.path.join("Images", f"{n}-1.jpg")
            new_1_path = os.path.join("Images", f"{sixth_group_n}-1.jpg")
            if os.path.exists(original_1_path):
                img = Image.open(original_1_path)
                img.save(new_1_path)
                print(f"Copied: {n}-1.jpg -> {sixth_group_n}-1.jpg")

# 更新meta.json文件
def update_meta_json():
    # 读取现有的meta.json
    meta_path = "meta.json"
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
    else:
        meta_data = {"Questions": [], "Answers": []}
    
    # 获取原始答案数据以保持一致性
    original_answers = meta_data.get("Answers", [])
    original_question_counts = meta_data.get("Question_Counts", {})
    
    # 清空现有的Questions和Answers
    meta_data["Questions"] = []
    meta_data["Answers"] = []
    
    # 生成新的Questions和Answers
    num_pairs = len(image_pairs)
    
    # 按照你的例子顺序：对每个原始图片，先列出它的所有变换版本
    for idx, original_n in enumerate(image_pairs):
        # 获取原始答案
        original_answer = ["S"]  # 默认值
        if idx < len(original_answers):
            if isinstance(original_answers[idx], list):
                original_answer = original_answers[idx]
            else:
                original_answer = [original_answers[idx]]
        
        # 原始图片
        meta_data["Questions"].append([
            f"./Images/{original_n}-0.jpg",
            f"./Images/{original_n}-1.jpg"
        ])
        meta_data["Answers"].append(original_answer)
        
        # 4个变换版本（答案相同）
        for i in range(4):
            transformed_n = original_n + (i + 1) * num_pairs
            meta_data["Questions"].append([
                f"./Images/{transformed_n}-0.jpg",
                f"./Images/{transformed_n}-1.jpg"
            ])
            meta_data["Answers"].append(original_answer)
        
        # 第6组（答案相反）
        sixth_group_n = original_n + 5 * num_pairs
        meta_data["Questions"].append([
            f"./Images/{sixth_group_n}-0.jpg",
            f"./Images/{sixth_group_n}-1.jpg"
        ])
        # 生成相反的答案
        opposite_answer = ["D"] if original_answer[0] == "S" else ["S"]
        meta_data["Answers"].append(opposite_answer)
    
    # 保存其他元数据
    if original_question_counts:
        meta_data["Question_Counts"] = original_question_counts
    
    # 更新总问题数
    meta_data["Total_Questions"] = len(meta_data["Questions"])
    
    # 保存更新后的meta.json到当前目录
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated meta.json with {len(meta_data['Questions'])} questions")
    print(f"Answer format example: {meta_data['Answers'][0] if meta_data['Answers'] else 'No answers'}")
    print(f"meta.json saved in current directory")

# 执行meta.json更新
update_meta_json()

print("Finished processing images and updating meta.json.")