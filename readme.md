# 简介

在使用`mm-wiki`过程中产生的脚本、想法以及修改记录

`mm-wiki`代码修改记录参阅 `代码修改记录.md`

## 批量上传想法

批量上传要考虑数据源

```
若为本地数据源, 则分为几类
    目录分类
        单目录
        多级目录
    文件格式分类
        html
        md
    图片分类
        base64图片
        外链图片
        本地图片
    文件排除
        如readme.md及其他无关的格式文件
        
若是网络资源, 则需根据实际网站进行判断,但仍需要考虑以下几点
    爬取的文章该如何分类
    文章的图片如何实现自动转换或自动上传wiki
```


### 目前已实现的脚本

```
1、单目录批量上传md文章
2、单目录批量html转md
3、转换md文档中的base64图片
4、单目录批量html转md,转换md内base64图片
5、单目录批量html转md,转换md内base64图片,并自动上传转换后的md
6、批量验证图片存活
7、批量验证文章内容是否为空
8、自动识别图片类型并保存到本地
9、单图片上传
10、单图片附件删除
11、批量删除图片附件
12、单目录批量上传md文章，含图片上传
13、批量删除空间内所有分类及文章，通过添加mm-wiki接口实现
    原代码已实现删除文章时自动删除相应图片,但不会删除图片目录
        检查images目录内所有空目录：find images -type d -empty
        删除空目录：find images -type d -empty | xargs rm -rf
14、本地多层目录批量上传md文章，全部上传同一目录
15、本地多层目录批量上传md文章，需识别本地目录并在wiki创建相应目录，并上传wiki到相应目录
16、本地多层目录批量上传md文章, 需自动识别图片类型并保存到本地
17、本地多层目录批量上传md文章, 需自动识别图片类型并上传wiki
18、本地多层目录批量上传md文章, 需自动识别图片类型并保存到本地及上传wiki
19、批量将某个目录A下的所有目录和文章移动到另一个目录B下
```
### 未实现的脚本
```
1、本地多层目录自动实现html转md
2、本地多层目录自动实现html转md, 需自动识别图片类型并保存到本地
3、本地多层目录自动实现html转md, 需自动识别图片类型上传wiki
4、本地多层目录自动实现html转md, 需自动识别图片类型并保存到本地及上传wiki
5、网络爬虫脚本
```

### 操作数据库

```
1、批量将某个目录A下的所有目录和文章移动到另一个目录B下,而后删除被移动的目录A
	修改目录的上层ID，并将目录移动到相应的目录下面，看能否达成目标
	结果：仅修改mw_document.parent_id字段就能完成索引移动，但本地文件需要手动移动并修改mw_document.path字段值
2、本地md文档上传到wiki目录内，通过修改数据库完成文章索引、图片索引可以忽略
	在mw_document新建一行数据,并保证相应数据填写正确，可以达到导入任务的目的
	结果：可以完成，但后续难点在于索引的处理
```

### wiki升级优化建议

```
可将mm-wiki作为后端提交、新增前台展示界面    未开始
```

可以参考: [如何系统化管理Hexo博客](https://maiernte.github.io/how-to-manage-big-hexo-blog.html)

想要实现这个功能，需要对wiki文章进行分类，区分可公开和不可公开两类，然后将可公开的部分通过hexo分享出去。

因为我的分类还是比较多的，这样使用起来太麻烦，遂放弃了。

## 20250414-wiki建设

部署方式有两种

- 本地部署：漏洞文档存储在本地，方便离线阅览(直接copy到硬盘即可)
- 数据库部署：漏洞文档存储在数据库

本地部署缺点

- 文档名称不能任意定义。如不能出现特殊字符，在linux中`/`会被认为是目录分割符号；在windows中不能出现`<>`等。
- 索引问题。本地部署需要严格的索引，如mm-wiki的形式，对后期维护更新增加很多麻烦
- 数据大小问题。通过本地数据，md文档以及上传的附件、图片等动辄就几个G

数据库部署

- 暂未找到合适的系统

# 项目使用

## 目录结构

```
│  main.py
│  readme.md
│  requirement.txt
│  代码修改记录.md
│  Identify_pictures.py
├─config
│      config.json
├─lib
│      config_loader.py
│      hander_random.py
│      logger_init.py
│      logo.py
│      Parallel_Processing.py
├─logs
│  │  image_extraction.csv
│  └─20250430
│          error_20250430.log
│          log_20250430.log
└─modules
│      Document_Delete_all.py
│      Document_GetId.py
│      Document_Index.py
│      Document_MoveDirectory.py
│      Document_page_modify.py
│      Document_save.py
│      Document_Sort.py
│      Getimg_Isalive.py
│      Login.py
│      Modify_Image.py
```

## 命令参数

### 识别处理md文档内图片

`Identify_pictures.py`

```bash
python3 .\Identify_pictures.py -h
usage: Identify_pictures.py [-h] -path PATH_NAME [-t THREAD] [-proxy PROXY_NAME] [-w]

optional arguments:
  -h, --help         show this help message and exit
  -path PATH_NAME    请输入文档根目录,默认脚本所在目录
  -t THREAD          请输入线程
  -proxy PROXY_NAME  请输入socks5 ip及端口,eg socks5://127.0.0.1:7890
  -w, --write        是否将修改写入文件
```

使用示例

```bash
# 基础使用 debug模式, 若指定了proxy则先使用代理测试图片能否访问，若失败则使用本地网络测试。可以查看日志文件进行调整
python3 .\Identify_pictures.py -path ”d:\123“ -proxy 127.0.0.1:7890

# 加入线程
python3 .\Identify_pictures.py -path ”d:\123“ -proxy 127.0.0.1:7890 -t 10

# 标准使用 加入-w参数，用来将图片修改后的数据同步到md文档
python3 .\Identify_pictures.py -path ”d:\123“ -proxy 127.0.0.1:7890 -w
```

### wiki主程序

`main.py`

```bash
usage: main.py [-h] [-path PATH_NAME] [-id DOCUMENT_MAX] [-sid SPACE_ID] [-pid PARENT_ID] [-t THREAD] -m
               {status,login,add,delall,move,sort,alive} [-tid TARGET_ID] [-delete_parent {true,false}]
               [-recursive {true,false}] [-only_docs {true,false}]

MM-Wiki文档自动上传工具

optional arguments:
  -h, --help            show this help message and exit
  -path PATH_NAME       请输入文档根目录路径（支持包含空格的路径）
  -id DOCUMENT_MAX      请输入文档ID或范围,eg: 4385 or 784-4385
  -sid SPACE_ID         请输入空间ID，默认为1
  -pid PARENT_ID        请输入目录ID
  -t THREAD             线程池大小，默认为1
  -m {status,login,add,delall,move,sort,alive}
                        执行模式：status-检测cookie，login-仅登录，add-写入文档，delall-删除目录下所有文档，move-移动目录,sort-排序,alive-检测图片链接是否可访问
  -tid TARGET_ID        移动模式的目标目录ID
  -delete_parent {true,false}
                        删除模式是否删除父目录：true-父目录(默认)，false-不删除
  -recursive {true,false}
                        是否递归排序子目录：true-递归子目录(默认)，false-不递归
  -only_docs {true,false}
                        移动模式是否仅移动文档：true-仅移动文档，false-移动所有内容(默认)
```

#### 全局认证

```bash
# 检测cookie是否有效, 项目全部相关功能通过cookie进行认证
python3 .\main.py -m status

# 如果cookie无效, 可以使用login更新cookie, 登录成功会同步更新配置文件中的cookie值
python3 .\main.py -m login
```

配置文件`config/config.json`

- `TARGET_BASE_URL（必须）`：平台URL
- `USERNAME`（必须）`：账号
- `PASSWORD`（必须）`：密码
- `COOKIE`：可选

```bash
    "TASK": {
        "TARGET_BASE_URL": "http://192.168.1.1:8080",
        "USERNAME": "admin",
        "PASSWORD": "123456",
        "COOKIE": "mmwikissid=cbcbc8ea70500824af9728a5eab24dd7; mmwikipassport=n8sckEYYgdC1h4iJgdgGgEgXhwrShzech7iGiFlHy41Di45JiAuxyda=",
```

#### 自动上传

上传本地文档到平台，若指定目录存在子目录，则自动在平台创建相应子目录及文档

不足：暂未加入图片自动处理模块，因此`尽量`保证上传的文档图片正常访问。这方面可以使用`Identify_pictures`单独调试

参数选项

- `path（必须）`：本地文档路径
- `sid（必须）`：空间ID，可以修改代码默认值
- `pid（必须）`：目录ID

```bash
# 上传本地123目录内所有文档到平台，空间ID为1，目录ID为222
python3 .\main.py -m add -path "d:\123" -sid 1 -pid 222

# sid 使用默认值
python3 .\main.py -m add -path "d:\123" -pid 222

# 加入线程, 默认为1
python3 .\main.py -m add -path "d:\123" -sid 1 -pid 222 -t 5
```

#### 删除目录内数据

删除平台指定目录所有文档及子目录

参数选项

- `sid（必须）`：空间ID，可以修改代码默认值
- `pid（必须）`：目录ID
- `delete_parent（可选）`：控制是否要删除指定的父目录，默认为true(删除)

```bash
# 上传本地123目录内所有文档到平台，空间ID为1，目录ID为222
python3 .\main.py -m delall "d:\123" -sid 1 -pid 222

# sid 使用默认值
python3 .\main.py -m delall "d:\123" -pid 222

# 删除指定目录数据，但不删除父目录
python3 .\main.py -m delall "d:\123" -pid 222 -delete_parent false
```

#### 移动目录内数据

移动目录内文档和子目录到另一个指定目录，如果目标目录与源目录存在相同文件则会跳过相应文件

参数选项

- `pid（必须）`：源目录ID
- `tid（必须）`：目标目录ID
- `only_docs（可选）`: 决定是否仅移动文档的参数，默认为false(移动所有数据)

```bash
# 将123内所有文档及子目录相关数据移动到456
python3 .\main.py -m move -pid 123 -tid 456

# 仅移动123内所有文档到456，遇到子目录则跳过
python3 .\main.py -m move -pid 123 -tid 456 -only_docs true
```

#### 对目录进行排序

按名称对指定父目录下的文档和目录进行排序，支持递归排序子目录（通过 recursive 参数控制）

- 排序规则：先显示目录，再显示文档；每种类型内部按名称字母顺序排序

参数选项

- `sid（必须）`：空间ID，可以修改代码默认值
- `pid（必须）`：目录ID
- `recursive`：是否递归排序子目录（可选，默认为 true）

```bash
# 对指定父目录222下的文档和目录进行排序
python3 .\main.py -m sort "d:\123" -sid 1 -pid 222

# sid 使用默认值
python3 .\main.py -m sort "d:\123" -pid 222

# 仅对指定父目录222下的文档和目录进行排序，不递归子目录
python3 .\main.py -m sort "d:\123" -pid 222 -recursive false
```

#### 检查图片链接是否可访问

检测平台文章内图片链接存活，可以使用`alive`模块

前提

- 空间需开启`允许分享`功能

参数选项

- `id（必须）`：文档ID或范围(4385 or 784-4385)
- `pid（必须）`：目录ID
- `recursive`：是否递归排序子目录（可选，默认为 true）

```
python39 main.py -m alive -t 100 -id 9999

2025-04-30 15:03:37,627 - INFO - 已提取: 9999/9999
2025-04-30 15:03:37,640 - INFO - 第一阶段完成，共从 3276 个文档中提取到 12504 张图片
2025-04-30 15:03:37,652 - INFO - 第一阶段结果已保存到: logs/image_extraction.csv

是否继续进行第二阶段验证？(Y/N):
```

第二阶段是验证图片存活

- 将第一阶段获取的链接分为内部链接和外部链接
- 外部链接直接标记为无效，避免不必要的验证
- 内部链接批量处理，减少重复操作

```
是否继续进行第二阶段验证？(Y/N): y
2025-04-30 15:43:34,839 - INFO - 第二阶段：开始验证所有图片链接...
2025-04-30 15:44:30,475 - INFO - 已验证: 10/261 个文档的图片
2025-04-30 15:48:17,383 - INFO - 已验证: 20/261 个文档的图片
2025-04-30 15:51:26,963 - INFO - 已验证: 30/261 个文档的图片
2025-04-30 15:55:42,730 - INFO - 已验证: 40/261 个文档的图片
2025-04-30 15:59:37,668 - INFO - 已验证: 50/261 个文档的图片
```

缺点

- 第二阶段比较慢，如果图片比较多，建议提取`image_extraction.csv`内地址，使用其他工具验证

