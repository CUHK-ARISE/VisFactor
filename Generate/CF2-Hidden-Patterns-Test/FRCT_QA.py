from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import argparse
import base64
import copy
import json
import os
import pickle
import requests
import time
from PIL import Image, ImageEnhance
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import random
import io
from IPython.display import display

_MAX_TRY = 5
_SLEEP = 0

help_dict = {
    'one': '1',
    'two': '2',
    'three': '3',
    'four': '4',
    'five': '5',
    'six': '6',
    'seven': '7',
    'eight': '8',
    'nine': '9',
    'zero': '0',
    'first': '1',
    'second': '2',
    'thirs': '3',
    'fourth': '4',
    'fifth': '5',
    'sixth': '6',
    'seventh': '7',
    'eighth': '8',
    'ninth': '9',
    'zeroth': '0'
}


def add_random_noise(image, noise_factor=0.1):
    image_array = np.array(image)
    noise = np.random.normal(loc=0.0, scale=noise_factor, size=image_array.shape)
    noisy_image = np.clip(image_array + noise * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_image)


def adjust_contrast(image, factor=1.5):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def adjust_brightness(image, factor=1.5):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def process_image_from_base64(base64_str, noise_factor=0.1, contrast_factor=1.5, brightness_factor=1.5):
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))

    img_with_noise = add_random_noise(image, noise_factor)
    img_with_contrast = adjust_contrast(img_with_noise, contrast_factor)
    img_with_brightness = adjust_brightness(img_with_contrast, brightness_factor)

    # img_with_brightness.show(title="Processed Image")
    buffered = BytesIO()
    img_with_brightness.convert("RGB").save(buffered, format="JPEG")
    jpeg_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jpeg_base64

def reverse_image_to_base64_jpeg(image_path):
    with Image.open(image_path) as img:
        reversed_img = img.transpose(Image.FLIP_LEFT_RIGHT)

        buffered = BytesIO()
        reversed_img.save(buffered, format="JPEG")

        reversed_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return reversed_base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def transform_image_with_random_position(base64_string):
    try:
        # Decode base64 to image
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        # Get original image dimensions
        width, height = image.size

        # Random rotation angle (-10 to +10 degrees)
        rotation_angle = random.uniform(-10, 10)

        # Rotate image to get its new dimensions
        rotated_image = image.rotate(rotation_angle, expand=True)
        rotated_width, rotated_height = rotated_image.size

        # Create new canvas (with extra margins)
        margin = 50  # Extra margin
        new_width = rotated_width + 2 * margin
        new_height = rotated_height + 2 * margin
        canvas = Image.new('RGB', (new_width, new_height), 'white')

        # Calculate center position with margin
        center_x = margin + (new_width - rotated_width) // 2
        center_y = margin + (new_height - rotated_height) // 2

        # Random horizontal shift (normal distribution)
        horizontal_shift = np.random.normal(loc=0, scale=5)
        vertical_shift = np.random.normal(loc=0,scale=5)
        # Paste rotated image onto the canvas
        canvas.paste(rotated_image, (int(center_x + horizontal_shift), int(center_y+vertical_shift)))

        # Convert to JPEG base64 encoding
        buffer = io.BytesIO()
        canvas.save(buffer, format='JPEG')
        result_base64 = base64.b64encode(buffer.getvalue()).decode()

        return result_base64

    except Exception as e:
        print(f"Error: {e}")
        return None


def judge_correct(gpt, label):
    if gpt == '':
        return False
    gpt = str(gpt).strip().lower()
    if type(label) == list:
        if gpt[:2] == 'a ' or gpt[:3] == 'an ' or gpt[:4] == 'the ':
            gpt = ' '.join(gpt.split()[1:])
        if gpt in label:
            return True
        return False
    label = str(label).strip().lower()
    if gpt == label:
        return True
    if label == 'yes':
        if gpt in ("yes", "true", "t", "y", "1"):
            return True
        return False
    if label == 'no':
        if gpt in ("no", "false", "f", "n", "0"):
            return True
        return False
    if label.isnumeric():
        if gpt in help_dict.keys() and help_dict[gpt] == label:
            return True
        return False
    return False

def show_pic(base64_string):
    # 解码Base64字符串
    image_data = base64.b64decode(base64_string)

    # 将解码后的数据转换为PIL图像
    image = Image.open(BytesIO(image_data))

    # 转换为numpy数组
    image_array = np.array(image)

    # 使用matplotlib展示图片
    plt.imshow(image_array)
    plt.axis('off')  # 不显示坐标轴
    plt.show()

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(_MAX_TRY))
def chat(payload):
    time.sleep(_SLEEP)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "
    }
    response = requests.post("http://152.69.226.145:3000/v1/chat/completions", 
                           headers=headers, 
                           json=payload)
    return response.json()

def transform_image(image_path, transform_type):
    """
    对图片进行变换
    transform_type: 0-3 表示旋转0,90,180,270度
                   4 表示水平镜像
                   5 表示竖直镜像
    """
    with Image.open(image_path) as img:
        if transform_type < 4:
            # 旋转
            rotated_img = img.rotate(transform_type * 90)
        elif transform_type == 4:
            # 水平镜像
            rotated_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            # 竖直镜像
            rotated_img = img.transpose(Image.FLIP_TOP_BOTTOM)
        
        buffered = BytesIO()
        rotated_img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def do_one_test(test_meta, test_mode, use_example, use_cot, test_prefix, debug_show_image=False):
    if test_mode == 'Split' and "Split" not in test_meta.keys():
        return

    examples = test_meta["Example"]
    example_content, example_content_save = [], []
    
    for eg in examples:
        if eg[0] == "Text":
            example_content.append(
                {
                    "type": "text",
                    "text": eg[1]
                }
            )
            example_content_save.append(
                {
                    "type": "text",
                    "text": eg[1]
                }
            )
        elif eg[0] == "Image":
            example_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(eg[1])}"
                    }
                }
            )
            example_content_save.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": eg[1]
                    }
                }
            )

    gpt_answers = []
    gpt_correct = 0
    gpt_invalid = 0
    all_count = 0
    
    for i, (q, a) in enumerate(zip(test_meta[test_mode]["Questions"], test_meta[test_mode]["Answers"])):
        question_results = []  # 存储每个问题的6种变换结果
        
        # 对每个问题都进行6种变换
        for transform_type in range(6):
            output_path = f"{test_prefix}-{i}-{transform_type}.json"
            if os.path.isfile(output_path):
                with open(f"{output_path[:-5]}.txt", 'r') as f:
                    all_count, gpt_correct, gpt_invalid = [int(_) for _ in f.read().splitlines()[2][5:].split(',')]
                with open(f"{output_path[:-5]}", "rb") as f:
                    gpt_answers = pickle.load(f)
                print(f"{output_path} exists. Continue. Recover: all_count: {all_count}, gpt_correct: {gpt_correct}, gpt_invalid: {gpt_invalid}")
                continue

            query_request = copy.deepcopy(QA_TEMPLATE)
            query_request_save = copy.deepcopy(QA_TEMPLATE)

            # Description
            query_content = [
                {
                    "type": "text",
                    "text": test_meta[test_mode]["Description"]
                }
            ]
            query_content_save = [
                {
                    "type": "text",
                    "text": test_meta[test_mode]["Description"]
                }
            ]

            # Example
            if use_example:
                query_content += example_content
                query_content_save += example_content_save

            # Instructions
            instruction = test_meta[test_mode]["Instruction"]
            if use_cot:
                instruction = instruction.replace('Please provide your answer', 'Let\'s think step by step. Please first give your explanation then provide your answer')
            query_content.append(
                {
                    "type": "text",
                    "text": instruction
                }
            )
            query_content_save.append(
                {
                    "type": "text",
                    "text": instruction
                }
            )

            # Questions
            for img in q:
                image_base64 = transform_image(img, transform_type)
                if debug_show_image:
                    print(f"\n显示变换类型 {transform_type} 的图片:")
                    show_pic(image_base64)
                query_content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                )
                query_content_save.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img
                        }
                    }
                )

            if test_meta["Name"] in ["Map-Planning-Test", "Surface-Development-Test"] and test_mode == "Split":
                query_content.append(
                    {
                        "type": "text",
                        "text": test_meta[test_mode]["Additional"][i][0]
                    }
                )
                query_content_save.append(
                    {
                        "type": "text",
                        "text": test_meta[test_mode]["Additional"][i][0]
                    }
                )

            # Ask GPT
            query_request["messages"][1]["content"] = query_content
            query_request_save["messages"][1]["content"] = query_content_save

            gpt_ans = ''
            for _ in range(0, _MAX_TRY):
                with open(f"{output_path[:-5]}.txt", 'w') as f:
                    print(query_request_save, file=f)
                full_json = chat(query_request)
                try:
                    gpt_ans_str = full_json['choices'][0]['message']['content']
                    gpt_ans_str = gpt_ans_str[gpt_ans_str.find('{'):gpt_ans_str.find('}') + 1]
                    if '[' in gpt_ans_str and ']' in gpt_ans_str and ',' in gpt_ans_str:
                        before = gpt_ans_str[:gpt_ans_str.find('[') + 1]
                        middle = gpt_ans_str[gpt_ans_str.find('[') + 1:gpt_ans_str.find(']')]
                        after = gpt_ans_str[gpt_ans_str.find(']'):]
                        middle = ['"' + _.strip().replace('"', '').replace("'", "") + '"' for _ in middle.split(',')]
                        middle = ', '.join(middle)
                        gpt_ans_str = before + middle + after
                    gpt_ans = json.loads(gpt_ans_str)['answer']
                except json.decoder.JSONDecodeError:
                    continue
                except KeyError:
                    continue
                else:
                    if gpt_ans == '': continue
                    with open(output_path, "w") as f:
                        json.dump(full_json, f, indent=4)
                    break

            if gpt_ans == '':
                with open(output_path, "w") as f:
                    json.dump(full_json, f, indent=4)
                gpt_invalid += len(a)
                question_results.append(False)
                continue

            # Analyze answer
            if type(gpt_ans) is not list:
                gpt_ans = [gpt_ans]
            gpt_answers.append(gpt_ans)
            print(f"{output_path[:-5]} response: {gpt_ans}")

            # 检查当前变换的结果是否正确
            transform_correct = True
            for output_a, label_a in zip(gpt_ans, a):
                judge_output = judge_correct(output_a, label_a)
                print(f"GPT: {output_a}, Label: {label_a}, Judge: {judge_output}")
                if not judge_output:
                    transform_correct = False
                    break
            
            question_results.append(transform_correct)
            
            with open(f"{output_path[:-5]}.txt", 'a') as f:
                f.write(f'\n#####{all_count},{gpt_correct},{gpt_invalid}')
            with open(f"{output_path[:-5]}", "wb") as f:
                pickle.dump(gpt_answers, f)

        # 只有当所有6种变换都正确时，才增加正确计数
        if len(question_results) == 6 and all(question_results):
            gpt_correct += len(a)
        all_count += len(a)

    accuracy = gpt_correct / all_count
    print(f"{test_prefix} accuracy: {accuracy}")
    invalid = gpt_invalid / all_count
    print(f"{test_prefix} invalid: {invalid}")
    
    with open(f"{test_prefix}.txt", "w") as f:
        for ans in gpt_answers:
            f.write(f"{ans}\n")
        f.write(f"\n{accuracy}\n")
        f.write(f"\n{invalid}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",
                        type=str,
                        default="Images",
                        help="root to the data",
                        )
    parser.add_argument("--flag",
                        type=str,
                        default="gpt4o-example-cot-group-0",
                        help="name of this run",
                        )
    parser.add_argument("--mode",
                        type=str,
                        choices=['Split', 'Group'],
                        default="Group",
                        help="Split or Group",
                        )
    parser.add_argument("--example",
                        action='store_true',
                        help="whether to provide example",
                        )
    parser.add_argument("--cot",
                        action='store_true',
                        help="whether to use cot",
                        )
    parser.add_argument("--key",
                        type=str,
                        default=''
                        )
    parser.add_argument("--model",
                        type=str,
                        default='gpt-4o-2024-11-20'
                        )
    parser.add_argument("--system",
                        type=str,
                        default='You are a helpful assistant.'
                        )
    parser.add_argument("--temperature",
                        type=float,
                        default=0.0
                        )
    parser.add_argument("--maxtoken",
                        type=int,
                        default=3000
                        )
    parser.add_argument("--debug_show_image",
                        action='store_true',
                        help="whether to show transformed images for debugging",
                        )
    opt = parser.parse_args()
    
    QA_TEMPLATE = {
        "model": opt.model,
        "messages": [
            {
                "role": "system",
                "content": opt.system
            },
            {
                "role": "user",
                "content": []
            }
        ],
        "temperature": opt.temperature,
        "max_tokens": opt.maxtoken
    }
    
    HEADER = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {opt.key}"
    }

    with open("meta.json", 'r') as f:
        data = json.load(f)
    for test_id, test in data.items():
        test_prefix = f"Results/{test_id}-{test['Name']}"

        if not os.path.isdir(test_prefix):
            os.makedirs(test_prefix)

        test_prefix += f'/{opt.flag}'
        
        do_one_test(
            test_meta=data[test_id],
            test_mode=opt.mode,
            use_example=opt.example,
            use_cot=opt.cot,
            test_prefix=test_prefix,
            debug_show_image=opt.debug_show_image
        )


