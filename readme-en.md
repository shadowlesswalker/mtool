by Shadow(山斗) from China.

### mtool(music tool) is a simple audio player mainly running on linux.

mtool is used with command line interface.you can control the player in your own code to play,stop musics.

mtool is C/S architecture program. it runs a UDP server at  the default port:127.0.0.1:6666 and receives commands from clients to control the player.

mtool use the config file ./mtool.conf . 

In mtool.conf , you can set the default values like volume,playing order,default playlist in the player section,
and set some playlists in the playlists section.Each playlist is a path in which should include music files.

We assume that you will put mtool codes in the path: /usr/mtool/ .

To use mtool ,make sure you have installed the dependencies below:

```
	pygame,configparser
```

You can start the server with command like this:

```
	python /usr/mtool/mtool.py --server start
```

To test if the server is running ,use the command like this:

```
	python /usr/mtool/mtool.py -c info
```

To close the server with command like this:    	

```
	python /usr/mtool/mtool.py -c exit
```

To play,stop,pause,resume music with command like this:

```
    python /usr/mtool/mtool.py -c play|stop|pause|resume
```

To set volume with command like this:

    	python /usr/mtool/mtool.py -c vol=0.5

To set what to do after current playing(stop,loop,random,next) with command like this:

   	    python /usr/mtool/mtool.py -c next=stop|loop|random|next

To play a specific music file with command like this:

    	python /usr/mtool/mtool.py -c playf=/var/share/music/qiansixi.mp3

To set the default playlist with command like this:

    	python /usr/mtool/mtool.py -c playlist=music   //music should be a playlist name.

main project files:

```
./ 

​	./mtool.py  //main python code 

​	./start    //a bash script to start mtool server,just run it with no any parameter

​	./mtoolctl    //a bash script to conveniently run commands .you just need to run code like this :
			mtoolctl -c play
	instead of:
			python /var/mtool/mtool.py -c play 
	
```

to use this script ,you can make a link from /bin/mtool to /usr/mtool/mtoolctl.

