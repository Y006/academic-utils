import os
import ast
import json

# 获取当前工作目录
current_dir = os.getcwd()

# 用来存储树形结构的字典
tree = {}

# 遍历目录，获取所有.py文件
for root, dirs, files in os.walk(current_dir):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            file_name = os.path.relpath(file_path, current_dir)

            # 读取 Python 文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            # 解析文件中的import语句
            imports = []
            try:
                tree_ast = ast.parse(file_content)
                for node in ast.walk(tree_ast):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        imports.append(node.module)
            except SyntaxError:
                imports = []

            # 生成树形结构
            file_tree = {
                "file_path": file_name,
                "imports": imports
            }

            # 将文件信息添加到树形结构
            tree[file_name] = file_tree

# 将树结构输出到JSON文件
output_file = os.path.join(current_dir, "file_tree_with_imports.json")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tree, f, indent=4, ensure_ascii=False)

print(f"Tree structure with imports has been saved to {output_file}")
