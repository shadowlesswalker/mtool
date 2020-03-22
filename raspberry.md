By  ShadowlessWalker(山斗)    2020-03-22

-----------------------------------------

买了个树莓派3B+，装好系统后灰落了好厚一层都不知道要干嘛。。。最近突发奇想：用树莓派做一个音乐播放器，每天6:30-7:20自动播放英语听力，强迫自己练习英语，也治治自己的懒床习惯，平时也可以用来听听歌。

# 准备工作：

1.树莓派一个，并且己安装好linux系统，并且己安装好Python3环境；

2.音箱一个（AUX有线接口或蓝牙音箱都行），连接到树莓派上；

# 软件环境搭建： 

[mtool](https://gitee.com/shadowlesswalker/mtool)是一个用python写的音乐播放器，在gitee和github上开源，主要用命令行进行控制，这个很适合我们这个需求。

下载地址：https://gitee.com/shadowlesswalker/mtool.git

首先我们在电脑上用ssh工具（我用的putty）登陆到树莓派，不会的可以另行百度树莓派ssh教程。输入以下命令：

**cd /usr**

**git clone https://gitee.com/shadowlesswalker/mtool.git  mtool  #下载mtool源代码**

**cd mtool**

**ln -s -f /usr/mtool/mtoolctl  /usr/bin/mtool  #创建软链接（快捷方式）**

然后安装mtool依赖包：pygame，configparser(有的话就不用安装了)

**sudo apt install python3-pygame**

**pip3 install configparser**

至此，mtool就算安装完成了。mtool是一个C/S(服务器/客户端)模式的程序，服务器开启后会监听UDP端口（默认为127.0.0.1:6666），然后接受来自客户端的命令去控制播放。

我再来设置一下服务器端的开机自启动:

**vim ~/.bashrc**

在最后面添加命令：

**nohup mtool --server start > /usr/mtool/log &    #其中nohup与&用于后台运行程序**

# 配置音乐文件夹路径

先来配置一下音乐文件夹的位置，打开/usr/mtool/mtool.conf，在里面自行修改：

***[player]     #这个节设置播放器参数
\***

***list = music   #设置默认的播放列表，列表名必须在后面的playlists节中出现
\***

***volume = 0.2  #默认音量
\***

***port = 6666   #默认UDP端口，用于服务器接受命令
\***

***index = 2    #当前播放位置
\***

***next = next   #默认播放模式：next|loop|random 对应顺序播放|单曲循环|随机播放
\***

***[playlists]    #播放列表预设节，可设置多个，格式为：列表名=文件夹路径
\***

***music = music    #播放列表名为music，路径为./music
\***

***en-listen = /var/share/en-listen  #我的英语听力资源文件的路径
\***

# **开始使用mtool命令\* \***

***source ~/.bashrc 
\***

***或\***

***\**nohup mtool --server start > /usr/mtool/log &\**
\***

***#先手动启动服务端，虽然前面配置了开机自启动，但也只能下次开机才能生效\***

***mtool -c info  #查看服务器状态，可用来测试服务器是否己启动，成攻类似如下显示：\***

![img](https://upload-images.jianshu.io/upload_images/22517118-dc792895814c24c5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**
mtool -c play #播放**

**mtool -c vol=0.5  #设置音量**

**mtool -c lists #查看可用的播放列表**

**mtool -c list   #列出当前播放列表中的音乐文件**

**mtool -c next=random|next|loop  #设置播放顺序**

**mtool -c playf=zui   #切换为单曲循环(next=loop)，并且播放文件名中包含zui的文件**

基本的用法就这样了，我们可以通过在电脑上控制树莓派播放音乐了，但是电脑老开着也不好，况且躺在床上怎么办呢？我们可以在手机上安装ssh工具，比如JuiceSSH（推荐），阿里云app。

# 设置树莓派定时播放 

我们使用linux内置的计划任务命令crontab来设置定时播放功能。

说到定时任务，那我们首先得确认自己树莓派的时间是准确的。嘿嘿嘿。。。可惜，树莓派的时间一般都是不准确的。。。因为一般电脑在断电后时钟会由CMOS电池供电继续跑，但是树莓派断电后时间就会丢失。即然时间都不准确，又怎么能正常执行定时任务呢。。。

所以我们首先解决时间问题-NTP(网络时间同步)

***dpkg-reconfigure tzdata***  #时区设置，配置文件在/etc/timezone，设置为中国上海时区

***date***  #查看时间，确保我们的时区为中国时区

开启NTP服务

**apt install ntp**

***ntpdate ntp.ntsc.ac.cn***    #同步中国国家授时中心新（NTP服务器ntp.ntsc.ac.cn）

或者在/etc/ntp.conf中添加ntp服务器地址

重启ntp服务：

**systemctl enable ntp  #ntp开机自启动
**

**systemctl start ntp   #启动ntp服务
**

**date  #查看系统时间，应该正确了
**

再来设置定时任务：

先写一个切换播放列表、改变音量、开时播放的脚本，用来被定时任务调用：

**vim /usr/mtool/start-en-listen**

脚本内容很简单：

**_dir="/usr/mtool"
**

**mtool -c playlist=en-listen  #切换到英语听力播放列表
**

**mtool -c vol=1.0       #音量放到最大（嘿嘿嘿）   
**

**mtool -c next=random  #设置随机播放
**

**mtool -c play   #开始播放**

接下来添加定时任务

crontab -e   #将打开编辑器，在最后添加定时任务：

30 6 * * * /usr/mtool/start-en-listen >> /usr/mtool/log.client    #每天早上6:30开始播放

20 7 * * * mtool -c stop             #每天早上7:20停止播放



## 终于。。。大功造成！！！！每天早上无法安心地睡懒觉啦啦啦！！！

当然，我们还可以添加几行代码，每天早上6:30自动关闭ssh服务，7:20再打开，这样想睡懒觉时就无法从手机ssh端关闭树莓派播放了，只能爬起来去拔电源嘿嘿嘿。。。。。