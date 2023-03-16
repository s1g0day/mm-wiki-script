项目地址: [https://github.com/phachon/mm-wiki](https://github.com/phachon/mm-wiki)

### 代码修复

#### 修改左边侧栏宽度

位置：`/mm-wiki/static/js/modules/common.js`

```
默认230，可以修改为536// west__size:                 230,
```

#### 修改项目地址

```
https://github.com/phachon/MM-Wiki
替换为
/
```

#### 修改mm-wiki

仅仅修改view目录下的的html

```
mm-wiki
替换为
个人wiki库
```

#### 文档日志不能正常显示

`app\models\log_document.go`

原代码 - 211行

```
rs, err = db.Query(where.Limit(limit, number).OrderBy("log_document_id", "DESC"))
```

修改为

```
//rs, err = db.Query(where.Limit(limit, number).OrderBy("log_document_id", "DESC"))
rs, err = db.Query(db.AR().From(Table_LogDocument_Name).Limit(limit, number).OrderBy("log_document_id", "DESC"))
```

进入到根目录重编译一下

```
go build ./
```

替换编译后的`mm-wiki`

#### mm-wiki升级修复文章名字含有特殊符号

```
        修复位置: app\controllers\page.go、app\controllers\document.go
        修复关键词: 文档名称格式不正确！
        修复代码: 
            match, err := regexp.MatchString(`[\\\\/:*?\"<>、|]`, name)
            match, err := regexp.MatchString(`[\\\\/:*?\"<>、|]`, newName)
        文章和目录名称不能包含` \ / : * ? " < > | 、`非法字符
        
        代码回退: 部分文章因文件名含有 / 符号, 被linux当作目录符创建了目录
            建议：
                方法1: 编写脚本爬取所有文章名字, 查看符合条件的目录是否存在异常, 与`文章内容缺失`检测脚本合并处理
                方法2: 接通过数据库文件搜索
                方法3: 逐个查看文档目录
    
        windows下不能使用的字符-9个: ` \  /  :  *  ?  "  <  >  |`
        linux下不能使用的字符` / `
```

### 批量上传想法

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

#### 目前已实现的脚本

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
```

#### 未实现的脚本

```
    2、自动识别图片类型并上传到wiki
    3、多目录批量上传md文章
    4、多目录批量上传md文章, 需自动识别图片类型并保存到本地
    5、多目录批量上传md文章, 需自动识别图片类型并上传wiki
    6、多目录批量上传md文章, 需自动识别图片类型并保存到本地及上传wiki
    7、多目录自动实现html转md
    8、多目录自动实现html转md, 需自动识别图片类型并保存到本地
    9、多目录自动实现html转md, 需自动识别图片类型上传wiki
    10、多目录自动实现html转md, 需自动识别图片类型并保存到本地及上传wiki
    11、网络爬虫脚本
    12、自动删除空间内所有文章及相应图片
        原代码已实现删除文章时自动删除相应图片,但不会删除图片目录
            检查images目录内所有空目录：find images -type d -empty
            删除空目录：find images -type d -empty | xargs rm -rf
    13、批量将某个目录A下的所有目录和文章移动到另一个目录B下,而后删除被移动的目录A
```

### wiki升级优化建议

```
可将mm-wiki作为后端提交、新增前台展示界面    未开始
```

