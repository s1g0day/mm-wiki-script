import os
import base64
import json
def create_tree(path):
    tree = {}
    for item in os.listdir(path):
        try:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                tree[item] = create_tree(item_path)
            else:
                with open(item_path, 'rb') as f:
                    tree[item] = base64.b64encode(f.read()).decode('utf-8')
        except (OSError, UnicodeDecodeError) as e:
            print(e)
    return tree
# 在指定路径下生成目录树字典
tree = create_tree('test\\')
# def format_tree(tree, indent=0):
#     for key, value in tree.items():
#         if isinstance(value, dict):
#             print('{}{}\\'.format(' ' * indent, key))
#             format_tree(value, indent + 4)
#         else:
#             print('{}{} - {}'.format(' ' * indent, key, value))
# format_tree(tree)

# print(json.dumps(tree, indent=4, ensure_ascii=False))

# 打印字典有多少层级
# def dict_level(dic, level=1):
#     max_level = level
#     for key, value in dic.items():
#         if isinstance(value, dict):
#             sub_level = dict_level(value, level + 1)
#             if sub_level > max_level:
#                 max_level = sub_level
#     return max_level
# print(dict_level(tree))  # 输出 3

# python 打印字典有多少层级，获取各层级名字并判断是目录还是文件
def print_dict_level(dic, level=1, current_level=1):
    for key, value in dic.items():
        if isinstance(value, dict):
            print(f"{'-' * level}{key}/ (目录，第{current_level}级)")
            print_dict_level(value, level + 1, current_level + 1)
        else:
            print(f"{'-' * level}{key} (文件，第{current_level}级)")
my_dict = {"a": {"b": {"c": 1}}, "d": 2}
print(f"{'-' * 1}my_dict/ (目录，第1级)")
print_dict_level(tree, 2, 2)