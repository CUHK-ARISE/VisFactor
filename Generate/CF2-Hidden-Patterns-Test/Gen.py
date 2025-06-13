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

def generate_main_path(grid_size=3, path_len=6, seed=None, min_segments=4):
    """生成主路径，确保至少有min_segments条线段"""
    if seed is not None:
        random.seed(seed)
    
    max_attempts = 100
    for attempt in range(max_attempts):
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
            if neighbors:
                path.append(random.choice(neighbors))
        
        # 检查生成的路径是否有足够的线段
        segs = set()
        for i in range(len(path)-1):
            a, b = path[i], path[i+1]
            seg = tuple(sorted([a, b]))
            segs.add(seg)
        
        if len(segs) >= min_segments:
            return path
    
    # 如果多次尝试都失败，强制生成足够长度的路径
    print(f"Warning: 经过{max_attempts}次尝试，仍无法生成{min_segments}条线段的路径，使用最后一次生成的路径")
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
    if not main_segs: return main_segs, None
    main_segs = set(main_segs)
    seg = random.choice(list(main_segs))
    main_segs.remove(seg)
    i1, j1 = divmod(seg[0], grid_size)
    i2, j2 = divmod(seg[1], grid_size)
    pt1 = ij2xy(i1, j1, grid_size, img_size, margin)
    pt2 = ij2xy(i2, j2, grid_size, img_size, margin)
    # 使用更粗的白线来擦除
    cv2.line(img, pt1, pt2, (255,255,255), 12, lineType=cv2.LINE_AA)
    return main_segs, seg

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

def apply_transformation(img, transform_type):
    """应用图像变换"""
    if transform_type == "original":
        return img
    elif transform_type == "rotate_90":
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif transform_type == "rotate_180":
        return cv2.rotate(img, cv2.ROTATE_180)
    elif transform_type == "rotate_270":
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif transform_type == "flip_horizontal":
        return cv2.flip(img, 1)
    else:
        return img

def check_pattern_contains_target(target_segs, test_segs):
    """检查测试图像是否包含目标图案的所有线段"""
    return target_segs.issubset(test_segs)

def create_balanced_sixth_image(main_segs, test_params, all_segments, grid_size, img_size, margin, transform):
    """为每对问题创建平衡的第6组图像"""
    # 统计前5组中包含主图案的数量
    contains_count = sum(1 for param in test_params if param["contains_main_path"])
    
    # 创建第6组图像
    base_img_6 = np.ones((img_size, img_size, 3), np.uint8) * 255
    
    if contains_count >= 3:
        # 如果包含的多，第6组生成不包含的
        # 随机删除一条主图线段
        main_segs_copy = set(main_segs)
        erased_seg = random.choice(list(main_segs_copy)) if main_segs_copy else None
        if erased_seg:
            main_segs_copy.remove(erased_seg)
        draw_segments(base_img_6, main_segs_copy, grid_size, img_size, margin, (0,0,0), 4)
        label_6 = "O"
        contains_main_path = False
    else:
        # 如果不包含的多，第6组生成包含的
        draw_segments(base_img_6, main_segs, grid_size, img_size, margin, (0,0,0), 4)
        label_6 = "X"
        contains_main_path = True
        erased_seg = None
    
    # 添加噪声线段
    noise_count = random.randint(2,4)
    noise = add_noise_segments(all_segments, main_segs, n_noise=noise_count)
    draw_segments(base_img_6, noise, grid_size, img_size, margin, (0,0,0), 4)
    
    # 应用变换
    transformed_img_6 = apply_transformation(base_img_6, transform)
    
    return transformed_img_6, label_6, contains_main_path, noise, erased_seg

def generate_one(n, all_segments, img_dir, num_imgs, grid_size=3, img_size=400, margin=60, path_len=None, min_segments=4):
    if path_len is None:
        path_len = random.randint(5,8)  # 增加路径长度范围以确保有足够线段
    
    # 使用固定种子确保可复现
    main_seed = n * 1000
    random.seed(main_seed)
    
    # 生成主路径，确保至少有min_segments条线段
    main_path = generate_main_path(grid_size, path_len, main_seed, min_segments)
    main_segs = path_to_segments(main_path, grid_size)
    
    # 如果线段数量仍然不够，重新生成
    retry_count = 0
    while len(main_segs) < min_segments and retry_count < 10:
        retry_count += 1
        path_len += 1
        main_path = generate_main_path(grid_size, path_len, main_seed + retry_count, min_segments)
        main_segs = path_to_segments(main_path, grid_size)
    
    print(f"主图{n}: 生成了{len(main_segs)}条线段 (要求至少{min_segments}条)")

    # 记录主图参数
    main_params = {
        "id": n,
        "main_path": main_path,
        "main_segs": list(main_segs),
        "grid_size": grid_size,
        "img_size": img_size,
        "margin": margin,
        "path_len": path_len,
        "main_seed": main_seed,
        "min_segments": min_segments,
        "actual_segments": len(main_segs),
        "original_n": num_imgs
    }

    # 生成基础主图
    base_img = np.ones((img_size, img_size, 3), np.uint8) * 255
    draw_segments(base_img, main_segs, grid_size, img_size, margin, (0,0,0), 4)
    
    # 变换类型
    transforms = ["original", "rotate_90", "rotate_180", "rotate_270", "flip_horizontal"]
    transform_names = ["原图", "旋转90°", "旋转180°", "旋转270°", "水平镜像"]
    
    # 为每种变换生成主图
    main_img_paths = []
    for i, (transform, name) in enumerate(zip(transforms, transform_names)):
        transformed_img = apply_transformation(base_img.copy(), transform)
        main_img_path = os.path.join(img_dir, f"{n + i * num_imgs}.jpg")
        cv2.imwrite(main_img_path, transformed_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        main_img_paths.append(main_img_path)
        print(f"  生成主图变换: {name}")

    # 生成问题图片
    all_test_params = []
    
    # 为每种变换生成测试图像
    for transform_idx, (transform, name) in enumerate(zip(transforms, transform_names)):
        test_params = []
        
        # 生成前5组测试图像 (n-0.jpg到n-4.jpg)
        for k in range(5):
            # 使用固定种子确保可复现
            test_seed = n * 1000 + k + 1
            random.seed(test_seed)
            
            base_img_k = np.ones((img_size, img_size, 3), np.uint8) * 255
            # 随机决定是否包含主图路径
            contains_main_path = random.random() < 0.5
            
            if contains_main_path:
                # 包含主图路径，标记为X
                draw_segments(base_img_k, main_segs, grid_size, img_size, margin, (0,0,0), 4)
                # 添加噪声线段
                noise_count = random.randint(2,4)
                noise = add_noise_segments(all_segments, main_segs, n_noise=noise_count)
                draw_segments(base_img_k, noise, grid_size, img_size, margin, (0,0,0), 4)
                label_k = "X"
                erased_seg = None
            else:
                # 不包含主图路径，标记为O
                # 随机删除一条主图线段
                main_segs_copy = set(main_segs)
                erased_seg = random.choice(list(main_segs_copy)) if main_segs_copy else None
                main_segs_no, _ = erase_main_line(base_img_k, main_segs, grid_size, img_size, margin)
                draw_segments(base_img_k, main_segs_no, grid_size, img_size, margin, (0,0,0), 4)
                # 添加噪声线段
                noise_count = random.randint(2,4)
                noise = add_noise_segments(all_segments, main_segs_no, n_noise=noise_count)
                draw_segments(base_img_k, noise, grid_size, img_size, margin, (0,0,0), 4)
                label_k = "O"
            
            # 应用相同的变换
            transformed_img_k = apply_transformation(base_img_k, transform)
            
            # 记录测试图参数
            test_param = {
                "id": f"{n + transform_idx * num_imgs}-{k}",
                "original_id": f"{n}-{k}",
                "transform": transform,
                "transform_name": name,
                "test_seed": test_seed,
                "contains_main_path": contains_main_path,
                "noise_segments": noise,
                "noise_count": noise_count,
                "erased_segment": erased_seg,
                "label": label_k
            }
            test_params.append(test_param)
            
            img_path_k = os.path.join(img_dir, f"{n + transform_idx * num_imgs}-{k}.jpg")
            cv2.imwrite(img_path_k, transformed_img_k, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # 生成第6组平衡图像 (n-5.jpg)
        random.seed(n * 1000 + 6)  # 固定种子
        transformed_img_6, label_6, contains_main_path_6, noise_6, erased_seg_6 = create_balanced_sixth_image(
            main_segs, test_params, all_segments, grid_size, img_size, margin, transform
        )
        
        # 记录第6组参数
        test_param_6 = {
            "id": f"{n + transform_idx * num_imgs}-5",
            "original_id": f"{n}-5",
            "transform": transform,
            "transform_name": name,
            "test_seed": n * 1000 + 6,
            "contains_main_path": contains_main_path_6,
            "noise_segments": noise_6,
            "noise_count": len(noise_6),
            "erased_segment": erased_seg_6,
            "label": label_6,
            "is_balanced": True  # 标记这是平衡生成的图像
        }
        test_params.append(test_param_6)
        
        img_path_6 = os.path.join(img_dir, f"{n + transform_idx * num_imgs}-5.jpg")
        cv2.imwrite(img_path_6, transformed_img_6, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        all_test_params.extend(test_params)
        
        # 打印统计信息
        contains_count = sum(1 for param in test_params if param["contains_main_path"])
        print(f"  {name}: X={contains_count}, O={6-contains_count}")
    
    # 添加参数到主图记录
    main_params["test_params"] = all_test_params
    main_params["transforms"] = transforms
    main_params["transform_names"] = transform_names
    main_params["main_img_paths"] = main_img_paths
    
    return [], [], main_params

def generate_sixth_group(all_generation_params, img_dir, num_imgs, all_segments, grid_size=3, img_size=400, margin=60):
    """生成第六组图像 - 完整的一组变换"""
    print("\n开始生成第六组图像...")
    
    # 第六组的主图ID从5n+1开始
    sixth_group_start = 5 * num_imgs + 1
    
    sixth_group_params = []
    
    for n in range(1, num_imgs + 1):
        # 第六组对应的主图ID
        sixth_main_id = sixth_group_start + n - 1
        
        # 获取原始主图的参数
        original_params = None
        for params in all_generation_params:
            if params["id"] == n:
                original_params = params
                break
        
        if not original_params:
            print(f"Warning: 找不到主图{n}的参数")
            continue
        
        # 复制原始主图参数
        sixth_params = {
            "id": sixth_main_id,
            "original_id": n,
            "main_path": original_params["main_path"],
            "main_segs": original_params["main_segs"],
            "grid_size": grid_size,
            "img_size": img_size,
            "margin": margin,
            "path_len": original_params["path_len"],
            "main_seed": original_params["main_seed"],
            "min_segments": original_params["min_segments"],
            "actual_segments": original_params["actual_segments"],
            "original_n": num_imgs,
            "is_sixth_group": True
        }
        
        # 生成第六组主图（与原图相同，不变换）
        main_segs = set(tuple(seg) if isinstance(seg, list) else seg for seg in original_params["main_segs"])
        base_img = np.ones((img_size, img_size, 3), np.uint8) * 255
        draw_segments(base_img, main_segs, grid_size, img_size, margin, (0,0,0), 4)
        
        main_img_path = os.path.join(img_dir, f"{sixth_main_id}.jpg")
        cv2.imwrite(main_img_path, base_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"  生成第六组主图: {sixth_main_id}.jpg (对应原图{n}.jpg)")
        
        # 生成第六组的测试图像（0-5）
        test_params = []
        for k in range(6):
            # 找到原始的测试图参数（原图变换，不是其他旋转）
            original_test_param = None
            for test_param in original_params["test_params"]:
                if test_param["original_id"] == f"{n}-{k}" and test_param["transform"] == "original":
                    original_test_param = test_param
                    break
            
            if not original_test_param:
                print(f"Warning: 找不到原始测试图{n}-{k}的参数")
                continue
            
            # 读取原始测试图
            original_img_path = os.path.join(img_dir, f"{n}-{k}.jpg")
            if not os.path.exists(original_img_path):
                print(f"Warning: 原始测试图{original_img_path}不存在")
                continue
            
            original_img = cv2.imread(original_img_path)
            
            # 生成平衡的测试图
            test_seed = original_test_param["test_seed"] + 10000  # 使用不同的种子
            random.seed(test_seed)
            
            # 平衡逻辑：与原来相反
            original_contains = original_test_param["contains_main_path"]
            
            if original_contains:
                # 原本包含主图（X） -> 第六组不包含（O）
                # 方法：先删除一条主图线段，再应用变换
                base_img_k = original_img.copy()
                
                # 先删除一条主图线段
                main_segs_for_erase = set(tuple(seg) if isinstance(seg, list) else seg for seg in main_segs)
                erased_seg = random.choice(list(main_segs_for_erase)) if main_segs_for_erase else None
                
                if erased_seg:
                    # 用白线擦除这条线段
                    i1, j1 = divmod(erased_seg[0], grid_size)
                    i2, j2 = divmod(erased_seg[1], grid_size)
                    pt1 = ij2xy(i1, j1, grid_size, img_size, margin)
                    pt2 = ij2xy(i2, j2, grid_size, img_size, margin)
                    cv2.line(base_img_k, pt1, pt2, (255,255,255), 12, lineType=cv2.LINE_AA)
                    
                    print(f"    {sixth_main_id}-{k}: 擦除线段{erased_seg}后应用变换 (原X->O)")
                else:
                    print(f"    {sixth_main_id}-{k}: 未找到可擦除的线段")
                
                # 然后应用旋转/镜像变换
                transforms = ["rotate_90", "rotate_180", "rotate_270", "flip_horizontal"]
                chosen_transform = random.choice(transforms)
                base_img_k = apply_transformation(base_img_k, chosen_transform)
                
                label_k = "O"
                contains_main_path = False
                transform_applied = f"erase_then_{chosen_transform}"
                
            else:
                # 原本不包含主图（O） -> 第六组包含（X）
                # 方法：在原图基础上补上被擦除的线段
                base_img_k = original_img.copy()
                
                # 补上被擦除的线段
                erased_seg = original_test_param.get("erased_segment")
                if erased_seg:
                    # 绘制被擦除的线段
                    erased_seg = tuple(erased_seg) if isinstance(erased_seg, list) else erased_seg
                    i1, j1 = divmod(erased_seg[0], grid_size)
                    i2, j2 = divmod(erased_seg[1], grid_size)
                    pt1 = ij2xy(i1, j1, grid_size, img_size, margin)
                    pt2 = ij2xy(i2, j2, grid_size, img_size, margin)
                    cv2.line(base_img_k, pt1, pt2, (0,0,0), 4, lineType=cv2.LINE_AA)
                    
                    print(f"    {sixth_main_id}-{k}: 补上线段{erased_seg} (原O->X)")
                else:
                    print(f"    {sixth_main_id}-{k}: 未找到被擦除的线段信息")
                
                label_k = "X"
                contains_main_path = True
                transform_applied = "add_erased_segment"
                erased_seg = None  # 这里不再有擦除的线段
            
            # 记录第六组测试图参数
            test_param = {
                "id": f"{sixth_main_id}-{k}",
                "original_id": f"{n}-{k}",
                "transform": "sixth_group",
                "transform_name": "第六组",
                "test_seed": test_seed,
                "contains_main_path": contains_main_path,
                "noise_segments": original_test_param.get("noise_segments", []),
                "noise_count": original_test_param.get("noise_count", 0),
                "erased_segment": erased_seg,
                "label": label_k,
                "is_sixth_group": True,
                "balanced_from": original_test_param["id"],
                "transform_applied": transform_applied,
                "original_answer": "X" if original_contains else "O"
            }
            test_params.append(test_param)
            
            # 保存第六组测试图
            img_path_k = os.path.join(img_dir, f"{sixth_main_id}-{k}.jpg")
            cv2.imwrite(img_path_k, base_img_k, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        sixth_params["test_params"] = test_params
        sixth_group_params.append(sixth_params)
        
        # 打印统计信息
        contains_count = sum(1 for param in test_params if param["contains_main_path"])
        original_contains_count = sum(1 for param in test_params if param["original_answer"] == "X")
        print(f"    第六组{sixth_main_id}: X={contains_count}, O={6-contains_count} (原图{n}: X={original_contains_count}, O={6-original_contains_count})")
    
    return sixth_group_params

def organize_questions_answers(all_generation_params, sixth_group_params, img_dir, n):
    """按指定顺序组织问题和答案"""
    questions = []
    answers = []
    
    # 合并所有参数（原5组 + 第6组）
    all_params = all_generation_params + sixth_group_params
    
    # 按照你要求的顺序排列：
    # 第k个测试图的所有变换（包括第6组），然后是第k+1个测试图的所有变换
    for k in range(6):  # 6个测试图 (0-5)
        for main_id in range(1, n + 1):  # 每个主图ID
            for transform_idx in range(6):  # 6个变换 (原图、90°、180°、270°、水平镜像、第六组)
                if transform_idx < 5:
                    # 前5组变换
                    main_img_path = os.path.join(img_dir, f"{main_id + transform_idx * n}.jpg")
                    test_img_path = os.path.join(img_dir, f"{main_id + transform_idx * n}-{k}.jpg")
                else:
                    # 第6组
                    sixth_main_id = 5 * n + main_id
                    main_img_path = os.path.join(img_dir, f"{sixth_main_id}.jpg")
                    test_img_path = os.path.join(img_dir, f"{sixth_main_id}-{k}.jpg")
                
                questions.append([main_img_path, test_img_path])
                
                # 从参数中找到对应的答案
                answer_found = False
                for params in all_params:
                    if transform_idx < 5:
                        # 前5组
                        if params["id"] == main_id:
                            for test_param in params["test_params"]:
                                if test_param["id"] == f"{main_id + transform_idx * n}-{k}":
                                    answers.append([test_param["label"]])
                                    answer_found = True
                                    break
                    else:
                        # 第6组
                        sixth_main_id = 5 * n + main_id
                        if params["id"] == sixth_main_id:
                            for test_param in params["test_params"]:
                                if test_param["id"] == f"{sixth_main_id}-{k}":
                                    answers.append([test_param["label"]])
                                    answer_found = True
                                    break
                    
                    if answer_found:
                        break
                
                if not answer_found:
                    print(f"Warning: 未找到答案 - 主图ID:{main_id}, 变换:{transform_idx}, 测试图:{k}")
                    answers.append(["O"])  # 默认答案
    
    return questions, answers

def update_meta_json(meta_path, questions, answers, generation_params):
    """更新meta.json文件"""
    # 创建新的meta.json结构
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
                "Questions": questions,
                "Answers": answers
            },
            "GenerationParams": generation_params
        }
    }
    
    # 确保目录存在
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    
    # 保存更新后的meta.json
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)
    
    print(f"meta.json已保存到: {meta_path}")

def recreate_image_from_params(params, output_path, all_segments):
    """根据参数重新生成图片"""
    grid_size = params["grid_size"]
    img_size = params["img_size"]
    margin = params["margin"]
    
    if "main_path" in params:
        # 重新生成主图
        main_segs = set(tuple(seg) if isinstance(seg, list) else seg for seg in params["main_segs"])
        img = np.ones((img_size, img_size, 3), np.uint8) * 255
        draw_segments(img, main_segs, grid_size, img_size, margin, (0,0,0), 4)
    else:
        # 重新生成测试图
        main_params = params["main_params"]
        main_segs = set(tuple(seg) if isinstance(seg, list) else seg for seg in main_params["main_segs"])
        
        img = np.ones((img_size, img_size, 3), np.uint8) * 255
        
        if params["contains_main_path"]:
            draw_segments(img, main_segs, grid_size, img_size, margin, (0,0,0), 4)
        else:
            if params["erased_segment"]:
                main_segs_no = main_segs.copy()
                erased = tuple(params["erased_segment"]) if isinstance(params["erased_segment"], list) else params["erased_segment"]
                main_segs_no.discard(erased)
                draw_segments(img, main_segs_no, grid_size, img_size, margin, (0,0,0), 4)
            else:
                draw_segments(img, main_segs, grid_size, img_size, margin, (0,0,0), 4)
        
        if "noise_segments" in params:
            noise_segs = [tuple(seg) if isinstance(seg, list) else seg for seg in params["noise_segments"]]
            draw_segments(img, noise_segs, grid_size, img_size, margin, (0,0,0), 4)
    
    cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return img

# 修改主程序
if __name__ == "__main__":
    num_imgs = int(input("请输入要生成的主图数量："))
    img_dir = os.path.join(os.getcwd(), "Images")
    os.makedirs(img_dir, exist_ok=True)
    all_segments = get_all_grid_segments(3)
    
    all_generation_params = []
    
    print("开始生成前5组图像...")
    for n in range(1, num_imgs+1):
        # 传入num_imgs参数
        _, _, main_params = generate_one(n, all_segments, img_dir, num_imgs)
        all_generation_params.append(main_params)
    
    # 生成第六组
    sixth_group_params = generate_sixth_group(all_generation_params, img_dir, num_imgs, all_segments)
    
    print("\n开始组织问题和答案...")
    # 按指定顺序组织问题和答案
    questions, answers = organize_questions_answers(all_generation_params, sixth_group_params, img_dir, num_imgs)
    
    print(f"\n生成了 {len(questions)} 个问题和 {len(answers)} 个答案")
    
    # 更新meta.json
    meta_path = os.path.join(os.getcwd(), "meta.json")
    all_params_for_json = all_generation_params + sixth_group_params
    update_meta_json(meta_path, questions, answers, all_params_for_json)
    
    print(f"全部图片已生成到Images文件夹，共生成{6 * num_imgs}组主图和{6 * num_imgs * 6}个测试图。")
    print("meta.json已更新，问题按指定顺序排列。")
    print("第6组图像已平衡生成，防止全选同一答案。")
    
    # 验证第6组是否正确生成
    print("\n验证第6组图像生成:")
    for n in range(1, min(3, num_imgs+1)):  # 只检查前3个主图
        sixth_main_id = 5 * num_imgs + n
        img_path = os.path.join(img_dir, f"{sixth_main_id}.jpg")
        if os.path.exists(img_path):
            print(f"✓ 主图 {img_path} 存在")
        else:
            print(f"✗ 主图 {img_path} 不存在")
        
        for k in range(6):
            test_img_path = os.path.join(img_dir, f"{sixth_main_id}-{k}.jpg")
            if os.path.exists(test_img_path):
                print(f"✓ 测试图 {test_img_path} 存在")
            else:
                print(f"✗ 测试图 {test_img_path} 不存在")