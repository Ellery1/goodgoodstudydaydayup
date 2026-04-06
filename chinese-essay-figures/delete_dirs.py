import os

# 定义figures目录路径
figures_dir = "e:\\python\\goodgoodstudydaydayup\\chinese-essay-figures\\figures"

# 遍历figures目录下的所有子目录
for subdir in os.listdir(figures_dir):
    subdir_path = os.path.join(figures_dir, subdir)
    
    # 确保是目录
    if os.path.isdir(subdir_path):
        # 删除目录及其所有内容
        import shutil
        shutil.rmtree(subdir_path)
        print(f"已删除目录: {subdir}")

print("处理完成！")