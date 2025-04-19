import os
from PIL import Image
import glob

def add_white_background(image_folder):
    # 获取所有PNG图片的文件路径
    image_files = glob.glob(os.path.join(image_folder, "*.png"))
    
    # 检查是否找到图片
    if not image_files:
        print(f"错误：在 {image_folder} 中没有找到PNG图片")
        return
    
    print(f"\n开始处理图片，添加白色背景...")
    
    # 遍历处理每张图片
    for image_path in image_files:
        try:
            img = Image.open(image_path)
            
            # 检查图片是否有透明通道
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # 创建白色背景
                white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                
                # 将原图合成到白色背景上
                if img.mode == 'P':
                    img = img.convert('RGBA')
                white_bg.paste(img, (0, 0), img)
                
                # 转换为RGB模式（去除Alpha通道）
                white_bg = white_bg.convert('RGB')
                
                # 保存修改后的图片
                white_bg.save(image_path)
                print(f"已处理: {os.path.basename(image_path)}")
            else:
                print(f"跳过: {os.path.basename(image_path)} (没有透明度)")
        
        except Exception as e:
            print(f"处理 {os.path.basename(image_path)} 时出错: {e}")

# 脚本与Images文件夹在同一目录下
script_dir = os.path.dirname(os.path.abspath(__file__))
image_folder = os.path.join(script_dir, "Images")

# 检查Images文件夹是否存在
if not os.path.exists(image_folder):
    print(f"错误: Images文件夹不存在于 {script_dir}")
else:
    print(f"找到Images文件夹: {image_folder}")
    add_white_background(image_folder)
