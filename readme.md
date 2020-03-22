By Shadow(山斗) 

### mtool(music tool) 是一个简单的用Python写的音乐播放器。

mtool主要是以**命令行方式**进行操作，你可以直接使用命令行，也可以在其它代码中调用命令行进行控制。

mtool是一个服务器/客户端模式的应用程序，服务器监听一个UDP端口（默认为127.0.0.1:6666），接受并执行来自客户端的命令。

依赖库: pygame , configparser

### 配置文件

mtool使用配置文件./mtool.conf来设置默认的音量、播放列表、播放模式、端口等。

```
[player]
list = music   #默认播放列表，列表名必须出现在playlists节中
volume = 0.2   #默认音量
port = 6666    #服务器端口
index = 2      #当前播放文件索引（相对于当前播放列表）
next = next    #播放模式next|loop|random 分别对应顺序播放|单曲循环|随机播放

[playlists]    #定义播放列表节，可设置多个列表，其名称必须唯一
music = music  #路径为./music/
en-listen = /var/share/en-listen    
```

### 基本用法示例

以linux平台为例，假设你的安装目录为/usr/mtool/

启动服务端：		

```
python  /usr/mtool/mtool.py --server start 
```

如果要在后台运行服务，执行命令：		

```
nohup python /usr/mtool/mtool.py --server start &
```

由于要输入的命令太长，为了简便，使用 ./mtoolctl 脚本以缩小命令长度，只需要建立一个软链接：

```
ln -s /usr/mtool/mtoolctl  /usr/bin/mtool
```

查看服务端状态：

```
mtool -c info
```

开始|暂停|继续播放:

```
mtool -c play|pause|resume
```

停止播放:

```
mtool -c stop
```

设置音量:

```
mtool -c vol=0.5
```

查看可用的播放列表:

```
mtool -c lists
```

切换播放列表：

```
mtool -c playlist=music
```

列出当前播放列表的内容：

```
mtool -c list
```

设置播放模式：

```
mtool -c next=random|next|loop
```

播放指定文件(自动切换为单曲循环，当前播放列表中任何一个列表项包含指定文件名即可)：

```
mtool -c playf=zui  //可匹配文件名中包含zui的的第一个文件
```

关闭服务端：

```
mtool -c exit
```

