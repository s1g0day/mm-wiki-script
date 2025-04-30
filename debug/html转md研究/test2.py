'''
markdown与HTML的互转的几个模块
    1、md转html
        markdown模块(推荐）
        md-to-html模块(不推荐）
    2、html转md
        tomd模块
        html2text模块(推荐）
        html2markdown模块
        html2md模块
    
    pandoc 软件
'''

md_datas = '''
    快捷键
    ---------------------------
    撤销：Ctrl/Command + Z
    重做：Ctrl/Command + Y
    加粗：Ctrl/Command + B
    斜体：Ctrl/Command + I
    标题：Ctrl/Command + Shift + H
    无序列表：Ctrl/Command + Shift + U
    有序列表：Ctrl/Command + Shift + O
    检查列表：Ctrl/Command + Shift + C
    插入代码：Ctrl/Command + Shift + K
    插入链接：Ctrl/Command + Shift + L
    插入图片：Ctrl/Command + Shift + G
    查找：Command + F
    替换：Command + G
    
    标题
    ---------------------------
    # 1级标题
    ## 2级标题
    ### 3级标题
    #### 四级标题 
    ##### 五级标题  
    ###### 六级标题
    
    文本样式
    ---------------------------
    *强调文本* _强调文本_
    
    **加粗文本** __加粗文本__
    
    ==标记文本==
    
    ~~删除文本~~
    
    > 引用文本
    
    H~2~O is是液体。
    
    2^10^ 运算结果是 1024。
    
    列表
    ---------------------------
    - 项目
      * 项目
        + 项目
    
    1. 项目1
    2. 项目2
    3. 项目3
    
    - [ ] 计划任务
    - [x] 完成任务
    
    链接
    ---------------------------
    链接: [link](https://mp.csdn.net).
    
    图片: ![Alt](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw)
    
    带尺寸的图片: ![Alt](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw =30x30)
    
    居中的图片: ![Alt](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw#pic_center)
    
    居中并且带尺寸的图片: ![Alt](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw#pic_center =30x30)
    
'''
html_datas = '''
<h2>快捷键</h2>
<p>撤销：Ctrl/Command + Z
重做：Ctrl/Command + Y
加粗：Ctrl/Command + B
斜体：Ctrl/Command + I
标题：Ctrl/Command + Shift + H
无序列表：Ctrl/Command + Shift + U
有序列表：Ctrl/Command + Shift + O
检查列表：Ctrl/Command + Shift + C
插入代码：Ctrl/Command + Shift + K
插入链接：Ctrl/Command + Shift + L
插入图片：Ctrl/Command + Shift + G
查找：Command + F
替换：Command + G</p>
<h2>标题</h2>
<h1>1级标题</h1>
<h2>2级标题</h2>
<h3>3级标题</h3>
<h4>四级标题</h4>
<h5>五级标题</h5>
<h6>六级标题</h6>
<h2>文本样式</h2>
<p><em>强调文本</em> <em>强调文本</em></p>
<p><strong>加粗文本</strong> <strong>加粗文本</strong></p>
<p>==标记文本==</p>
<p>~~删除文本~~</p>
<blockquote>
<p>引用文本</p>
</blockquote>
<p>H~2~O is是液体。</p>
<p>2^10^ 运算结果是 1024。</p>
<h2>列表</h2>
<ul>
<li>项目</li>
<li>
<p>项目</p>
<ul>
<li>项目</li>
</ul>
</li>
<li>
<p>项目1</p>
</li>
<li>项目2</li>
<li>
<p>项目3</p>
</li>
<li>
<p>[ ] 计划任务</p>
</li>
<li>[x] 完成任务</li>
</ul>
<h2>链接</h2>
<p>链接: <a href="https://mp.csdn.net">link</a>.</p>
<p>图片: <img alt="Alt" src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw" /></p>
<p>带尺寸的图片: <img alt="Alt" src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw =30x30" /></p>
<p>居中的图片: <img alt="Alt" src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw#pic_center" /></p>
<p>居中并且带尺寸的图片: <img alt="Alt" src="https://imgconvert.csdnimg.cn/aHR0cHM6Ly9hdmF0YXIuY3Nkbi5uZXQvNy83L0IvMV9yYWxmX2h4MTYzY29tLmpwZw#pic_center =30x30" /></p>
'''
# print(md_datas)
# print(html_datas)

def html2text_r(md_text):
    import html2text
    # md_text = open('ret.html', 'r', encoding='utf-8').read()

    markdown = html2text.html2text(md_text)
    with open('make2.md', 'w', encoding='utf-8') as file:
        file.write(markdown)
def tomd_r(md_text):

    from tomd import Tomd

    # md_text = open('ret.html', 'r', encoding='utf-8').read()
    markdown = Tomd(md_text).markdown
    with open('make.md', 'w', encoding='utf-8') as file:
        file.write(markdown)
def html2markdown_r(md_text):
    import html2markdown

    # md_text = open('ret.html', 'r', encoding='utf-8').read()

    markdown = html2markdown.convert(md_text)

    with open('make3.md', 'w', encoding='utf-8') as file:
        file.write(markdown)

