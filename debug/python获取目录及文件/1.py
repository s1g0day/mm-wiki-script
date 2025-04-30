import os
def print_directory_tree(root_path, padding='', index=1):
    # 获取目录下所有文件和文件夹
    directory_items = os.listdir(root_path)
    # 排序，先输出文件夹再输出文件
    directory_items.sort(key=lambda x: (not os.path.isdir(os.path.join(root_path, x)), x))
    # 遍历每一个文件或文件夹
    for i, item in enumerate(directory_items):
        # 构造路径
        item_path = os.path.join(root_path, item)
        # 判断是文件还是文件夹
        if os.path.isfile(item_path) and item.endswith('.md'):
            # 如果是md文件，打印文件名，并输出序号
            print(padding + '|-- ' + str(index) + '. ' + item)
            # 索引加1
            index += 1
        elif os.path.isdir(item_path):
            # 如果是文件夹，打印文件夹名，并递归调用自己
            print(padding + '|-- ' + str(index) + '. ' + item + '/')
            index = print_directory_tree(item_path, padding + '    ', index=index)
    return index
# 在这里指定需要遍历的根目录
root_path = r'F:\tools\漏洞POC\漏洞汇总（持续更新中）\更新中\iemotion-poc\POC'
# 调用函数并输出目录树
print_directory_tree(root_path)