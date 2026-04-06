import os
import re

# 定义figures目录路径
figures_dir = "e:\\python\\goodgoodstudydaydayup\\chinese-essay-figures\\figures"

# 遍历figures目录下的所有子目录
for subdir in os.listdir(figures_dir):
    subdir_path = os.path.join(figures_dir, subdir)
    
    # 确保是目录
    if not os.path.isdir(subdir_path):
        continue
    
    # 检查是否存在profile.md文件
    profile_path = os.path.join(subdir_path, "profile.md")
    if not os.path.exists(profile_path):
        continue
    
    # 读取profile.md文件内容
    with open(profile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题中的人物中文名
    # 匹配以#开头的行，获取标题内容
    lines = content.split('\n')
    title_line = None
    for line in lines:
        if line.startswith('# '):
            title_line = line
            break
    
    if title_line:
        # 提取标题内容，去除#和空格
        title = title_line[2:].strip()
        # 提取中文名字部分，去除括号及内容
        chinese_name = re.split(r'\s*\(', title)[0].strip()
        
        # 构建目标文件路径
        target_path = os.path.join(figures_dir, f"{chinese_name}.md")
        
        # 写入文件
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已处理: {subdir} -> {chinese_name}.md")
    else:
        print(f"无法提取标题: {subdir}")

# 删除所有空的子目录
for subdir in os.listdir(figures_dir):
    subdir_path = os.path.join(figures_dir, subdir)
    if os.path.isdir(subdir_path):
        # 检查目录是否为空
        if not os.listdir(subdir_path):
            os.rmdir(subdir_path)
            print(f"已删除空目录: {subdir}")

print("处理完成！")