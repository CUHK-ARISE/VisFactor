import cv2
import numpy as np
import random
import os
import json

def get_all_grid_segments(grid_size=3):
    """返回所有合法的格点间线段（不含自环），输出为(indexA, indexB)形式，index=行*grid_size+列"""
    segments = []
    for i1 in range(grid_size):
        for j1 in range(grid_size):
            idx1 = i1 * grid_size + j1
            for i2 in range(grid_size):
                for j2 in range(grid_size):
                    idx2 = i2 * grid_size + j2
                    if idx1 != idx2:
                        seg = tuple(sorted([idx1, idx2]))
                        if seg not in segments:
                            segments.append(seg)
    return segments

def ij2xy(i, j, grid_size, img_size, margin):
    gap = (img_size - 2 * margin) // (grid_size - 1)
    x = margin + j * gap
    y = margin + i * gap
    return (x, y)

def generate_main_path(grid_size=3, path_len=6):
    idx = random.randint(0, grid_size*grid_size-1)
    path = [idx]
    for _ in range(path_len-1):
        i, j = divmod(path[-1], grid_size)
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0: continue
                ni, nj = i+di, j+dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    neighbors.append(ni*grid_size + nj)
        path.append(random.choice(neighbors))
    return path

def path_to_segments(path, grid_size):
    segs = set()
    for i in range(len(path)-1):
        a, b = path[i], path[i+1]
        seg = tuple(sorted([a, b]))
        segs.add(seg)
    return segs

def draw_segments(img, segs, grid_size, img_size, margin, color, thickness):
    for a, b in segs:
        i1, j1 = divmod(a, grid_size)
        i2, j2 = divmod(b, grid_size)
        pt1 = ij2xy(i1, j1, grid_size, img_size, margin)
        pt2 = ij2xy(i2, j2, grid_size, img_size, margin)
        cv2.line(img, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)

def erase_main_line(img, main_segs, grid_size, img_size, margin):
    if not main_segs: return main_segs
    main_segs = set(main_segs)
    seg = random.choice(list(main_segs))
    main_segs.remove(seg)
    i1, j1 = divmod(seg[0], grid_size)
    i2, j2 = divmod(seg[1], grid_size)
    pt1 = ij2xy(i1, j1, grid_size, img_size, margin)
    pt2 = ij2xy(i2, j2, grid_size, img_size, margin)
    cv2.line(img, pt1, pt2, (255,255,255), 16, lineType=cv2.LINE_AA)
    return main_segs

def add_noise_segments(all_segments, main_segs, n_noise=3):
    candidates = [s for s in all_segments if s not in main_segs]
    chosen = set()
    segs = []
    while len(segs) < n_noise and candidates:
        s = random.choice(candidates)
        if s not in chosen and s[::-1] not in chosen:
            segs.append(s)
            chosen.add(s)
    return segs

def generate_one(n, all_segments, img_dir, grid_size=3, img_size=400, margin=60, path_len=None):
    if path_len is None:
        path_len = random.randint(4,7)
    main_path = generate_main_path(grid_size, path_len)
    main_segs = path_to_segments(main_path, grid_size)

    # 保存主图
    img = np.ones((img_size, img_size, 3), np.uint8) * 255
    draw_segments(img, main_segs, grid_size, img_size, margin, (0,0,0), 8)
    main_img_path = os.path.join(img_dir, f"{n}.png")
    cv2.imwrite(main_img_path, img)

    # 生成问题图片
    questions = []
    answers = []
    
    # 生成n-0.png到n-4.png，并与主图配对
    for k in range(5):
        img_k = np.ones((img_size, img_size, 3), np.uint8) * 255
        # 随机决定是否包含主图路径
        contains_main_path = random.random() < 0.5
        
        if contains_main_path:
            # 包含主图路径，标记为X
            draw_segments(img_k, main_segs, grid_size, img_size, margin, (0,0,0), 8)
            # 添加噪声线段
            noise = add_noise_segments(all_segments, main_segs, n_noise=random.randint(2,4))
            draw_segments(img_k, noise, grid_size, img_size, margin, (0,0,0), 8)
            label_k = "X"
        else:
            # 不包含主图路径，标记为O
            # 随机删除一条主图线段
            main_segs_no = erase_main_line(img_k, main_segs, grid_size, img_size, margin) or main_segs
            draw_segments(img_k, main_segs_no, grid_size, img_size, margin, (0,0,0), 8)
            # 添加噪声线段
            noise = add_noise_segments(all_segments, main_segs_no, n_noise=random.randint(2,4))
            draw_segments(img_k, noise, grid_size, img_size, margin, (0,0,0), 8)
            label_k = "O"
        
        img_path_k = os.path.join(img_dir, f"{n}-{k}.png")
        cv2.imwrite(img_path_k, img_k)
        
        # 将主图和n-k.png作为一个问题组
        questions.append([main_img_path, img_path_k])
        answers.append([label_k])
    
    return questions, answers

def update_meta_json(meta_path, questions, answers):
    # 如果meta.json不存在，创建一个新的
    if not os.path.exists(meta_path):
        meta = {
            "CF2": {
                "Name": "Hidden-Patterns-Test",
                "Example": [
                    ["Text", "Look at the example below:"],
                    ["Image", "Images/CF2-Hidden-Patterns-Test/Example/1.jpg"],
                    ["Image", "Images/CF2-Hidden-Patterns-Test/Example/2.jpg"],
                    ["Text", "In the second image, when the model appears, it is shown by heavy lines. Therefore, the answer is: O, X, O, O, X, O, O. Now try this example:"],
                    ["Image", "Images/CF2-Hidden-Patterns-Test/Example/1.jpg"],
                    ["Image", "Images/CF2-Hidden-Patterns-Test/Example/3.jpg"],
                    ["Text", "The first, third, fourth, eighth, and tenth patterns contain the model. The second, fifth, sixth, seventh, and ninth do not contain the model. Therefore, the answer is: X, O, X, X, O, O, O, X, O, X."]
                ],
                "Group": {
                    "Description": "How quickly can you recognize a figure that is hidden among other lines? Each problem in this test contains an image of a model and another image of a pattern. You are to look for the model in the first image from the pattern in the second image. The model must always be in the given position, not on its side or upside down. You are to answer \"X\" if the model appears in the pattern or answer \"O\" if the model does not appear.",
                    "Instruction": "For the question below: Please provide your answer in the following JSON format: {\"answer\": \"X_or_O\"}.",
                    "Questions": [],
                    "Answers": []
                }
            }
        }
    else:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    
    # 更新CF2部分
    if "CF2" not in meta:
        meta["CF2"] = {
            "Name": "Hidden-Patterns-Test",
            "Example": [
                ["Text", "Look at the example below:"],
                ["Image", "../../Images/CF2-Hidden-Patterns-Test/Example/1.jpg"],
                ["Image", "../../Images/CF2-Hidden-Patterns-Test/Example/2.jpg"],
                ["Text", "In the second image, when the model appears, it is shown by heavy lines. Therefore, the answer is: O, X, O, O, X, O, O. Now try this example:"],
                ["Image", "../../Images/CF2-Hidden-Patterns-Test/Example/1.jpg"],
                ["Image", "../../Images/CF2-Hidden-Patterns-Test/Example/3.jpg"],
                ["Text", "The first, third, fourth, eighth, and tenth patterns contain the model. The second, fifth, sixth, seventh, and ninth do not contain the model. Therefore, the answer is: X, O, X, X, O, O, O, X, O, X."]
            ],
            "Group": {
                "Description": "How quickly can you recognize a figure that is hidden among other lines? Each problem in this test contains an image of a model and another image of a pattern. You are to look for the model in the first image from the pattern in the second image. The model must always be in the given position, not on its side or upside down. You are to answer \"X\" if the model appears in the pattern or answer \"O\" if the model does not appear.",
                "Instruction": "For the question below: Please provide your answer in the following JSON format: {\"answer\": \"X_or_O\"}.",
                "Questions": [],
                "Answers": []
            }
        }
    
    # 更新问题和答案
    meta["CF2"]["Group"]["Questions"] = questions
    meta["CF2"]["Group"]["Answers"] = answers
    
    # 确保目录存在
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    
    # 保存更新后的meta.json
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4)

if __name__ == "__main__":
    num_imgs = int(input("请输入要生成的主图数量："))
    img_dir = os.path.join(os.getcwd(), "Images")
    os.makedirs(img_dir, exist_ok=True)
    all_segments = get_all_grid_segments(3)
    
    all_questions = []
    all_answers = []
    
    for n in range(1, num_imgs+1):
        questions, answers = generate_one(n, all_segments, img_dir)
        all_questions.extend(questions)
        all_answers.extend(answers)
    
    # 更新meta.json
    meta_path = os.path.join(os.getcwd(), "meta.json")
    update_meta_json(meta_path, all_questions, all_answers)
    
    print("全部图片已生成到Images文件夹，meta.json已更新。")