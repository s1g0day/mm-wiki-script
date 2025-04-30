'''
转自:https://zhuanlan.zhihu.com/p/546673564
'''
import os
import tkinter 
import tkinter.filedialog
from shutil import move 

def file_select():
    global file,fold_path,file_name,file_name_prefix
    window = tkinter.Tk()
    print('请选择被操作文件')
    file = tkinter.filedialog.askopenfilename()         # 选择文件
    window.destroy()                                    # 关闭 GUI 窗口 
    fold_path = os.path.dirname(file)                   # 获取文件路径
    file_name = os.path.basename(file)                  # 获取文件名
    file_name_prefix = os.path.splitext(file_name)[0]   # 获取文件前缀
    print("您选择的文件是：",file_name)

def file_transform():

    file_format = input('输入需要转换后的文件格式:')
    os.chdir(fold_path)                                  
    cmd_pandoc = "pandoc -o " + file_name_prefix + "." +  file_format + " " + file_name
    print("文件转换开始",cmd_pandoc)
    os.system(cmd_pandoc)
    print("文件转换结束")
    move(file_name_prefix + "." +  file_format,python_path) # 移动文件到脚本所在的目录下

if __name__ == '__main__':

    python_path = os.getcwd()                                   # 获取脚本当前的工作路径
    file_select()
    file_transform()
    print("转换后的文件位于脚本所在的同级目录下")