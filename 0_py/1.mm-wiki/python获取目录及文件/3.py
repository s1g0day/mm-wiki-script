#python编写程序，根据目录树自动创建目录或文件
import os
def create_dir_or_file(path, tree):
    if not os.path.exists(path):
        os.mkdir(path)
    for item in tree:
        item_path = os.path.join(path, item)
        if isinstance(tree[item], dict):
            create_dir_or_file(item_path, tree[item])
        else:
            with open(item_path, 'w') as f:
                f.write(tree[item])
# 示例目录树
tree = {
    'dir1': {
        'file1.txt': 'Hello, World!',
        'dir2': {
            'file2.txt': 'Python is awesome!'
        }
    }
}
# 在当前路径下创建目录树
create_dir_or_file('test\\', tree)