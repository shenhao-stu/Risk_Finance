import os
import re

def is_blank(file_content):
    """检查文件是否为空白"""
    return not file_content.strip()

def is_duplicate(file_content, seen_contents):
    """检查文件是否为重复内容"""
    if file_content in seen_contents:
        return True
    seen_contents.add(file_content)
    return False

def is_low_quality(file_content, min_length=500):
    """检查文件是否为低质量内容（长度不足）"""
    return len(file_content) < min_length

def contains_chinese_characters(file_content):
    """检查文件是否包含中文字符"""
    # 中文字符范围：\u4e00-\u9fff
    return bool(re.search(r'[\u4e00-\u9fff]', file_content))

def remove_specific_field(file_content, field="图片\n"):
    """删除特定字段"""
    return file_content.replace(field, '')

def is_special_text(file_content):
    """检查文件是否包含特殊文本"""
    return '黑猫消费者服务平台' in file_content

def format_text(text):
    """格式化文本，删除多余空格"""
    # 去除每行两端的空白，并将多余的空行去掉
    lines = text.splitlines()
    formatted_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(formatted_lines)

def process_files(input_directory, output_directory):
    seen_contents = set()
    valid_files = []

    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)
    
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_directory, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if is_blank(content):
                    continue
                elif is_duplicate(content, seen_contents):
                    continue
                elif is_special_text(content):
                    continue
                elif is_low_quality(content):
                    continue
                elif not contains_chinese_characters(content):
                    continue
                else:
                    content = remove_specific_field(content)
                    formatted_content = format_text(content)
                    valid_files.append((file_path, formatted_content))
    
    # 将保留下来的文件保存到输出目录并重新命名
    for index, (file_path, formatted_content) in enumerate(valid_files):
        new_name = f"sample_{index + 1}.txt"
        new_path = os.path.join(output_directory, new_name)
        with open(new_path, 'w', encoding='utf-8') as formatted_file:
            formatted_file.write(formatted_content)

# 使用时，调用函数并传递输入和输出文件夹路径
process_files('datasets/raw', 'datasets/cleaned')
