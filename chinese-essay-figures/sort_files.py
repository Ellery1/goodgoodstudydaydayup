import os
import re
import locale

# 尝试设置中文locale
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Chinese')
    except:
        pass

# 定义figures目录路径
figures_dir = "e:\\python\\goodgoodstudydaydayup\\chinese-essay-figures\\figures"

# 获取所有.md文件
md_files = [f for f in os.listdir(figures_dir) if f.endswith('.md')]

# 按首字拼音降序排序
md_files_sorted = sorted(md_files, key=lambda x: locale.strxfrm(x), reverse=True)

# 打印排序结果
print("按首字拼音降序排序后的文件列表：")
for i, file in enumerate(md_files_sorted, 1):
    print(f"{i}. {file}")

print("\n排序完成！")