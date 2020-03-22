'''
code by Shadow(山斗) from China.

mtool(music tool) is a simple audio player mainly running on linux.
mtool is used with command line interface.you can control the player in your own code to play,stop musics.
mtool is C/S architecture program. it runs a UDP server at  the default port:127.0.0.1:6666 and receives commands from clients to control the player.
mtool use the config file ./mtool.conf . 
In mtool.conf , you can set the default values like volume,playing order,default playlist in the player section,
and set some playlists in the playlists section.Each playlist is a path in which should include music files.

'''

import pygame
import time
import sys, getopt
from socket import *
import threading
import re
import configparser
import os
import random
_dir=os.path.dirname(os.path.abspath(__file__))
_conf_file=os.path.join(_dir,'./mtool.conf')

print('hello from mtool by shadow')
mfile='./qiansixi.mp3'
isactive=True  #True to run server normally, False to quit Server
server_status='stopped' #stopped|playing|paused
mnext='stop'  #what to do for the next playing:stop|next|loop|random

vol=0.5 #volume
mlist=[]  #audio paths of current playlist
mindex=0  #index of playlist for next play
mport=6666 #Server UDP port
playlist_name='default' #current playlist name
playlist_path=os.path.join(_dir,'music')

def loadlist(listname):
    '''
    load audios from a playlist,the palylist name must be specified in mtool.conf
    '''
    global mlist,mfile,playlist_name,playlist_path
    listpath=''
    conf=configparser.ConfigParser()
    conf.read(_conf_file)
    if listname in conf['playlists'].keys():
        playlist_name=listname
        playlist_path=conf['playlists'][playlist_name]
        if os.path.isabs(playlist_path)==False:
            playlist_path=os.path.join(_dir,playlist_path)
    else:
        print("invalid playlist name:%s"%(listname))
        return

    if os.path.exists(playlist_path):
        mlist.clear()
        for iroot,idir,flist in os.walk(playlist_path):
            for f in flist:
                 mlist.append(os.path.join(iroot,f))        
    else:
        print("playlist %s(%s) doesn't exist"%(listname,playlist_path))
    
    mindex=0
    if len(mlist)>0:
        mfile=mlist[0]
    print("load playlist %s(%s) from %s"%(listname,len(mlist),playlist_path))

def _init():
    global mlist, vol, mport,mnext
    conf=configparser.ConfigParser()
    conf.read(_conf_file)
    vol=float(conf['player']['volume'])
    print("volume:%s"%(vol))
    mport=int(conf['player']['port'])
    mindex=int(conf['player']['index'])
    mnext=conf['player']['next']
    loadlist( conf['player']['list'])
    pygame.mixer.init()



def play():
    global isactive,mfile,mlist,vol,mnext,mindex,server_status
    
    if mnext=='loop':
        pass
    elif mnext=='next':
        mindex=mindex+1
        if mindex >= len(mlist):
            mindex=0
        mfile=mlist[mindex]
    elif mnext=='random':
        mindex=random.randint(0,len(mlist)-1)
        mfile=mlist[mindex]

    
    try:
        print("vol:%s,next:%s,playing file %s"%(vol,mnext,mfile))    
        track=pygame.mixer.music.load(mfile)    
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play()
        server_status='playing'
    except Exception as e:
        print(e)
        

def stop():
    global server_status
    server_status='stopped'
    pygame.mixer.music.stop()
    print('music stopped')

def pause():
    global server_status
    server_status='paused'
    pygame.mixer.music.pause()
    print('music paused')
def unpause():
    global server_status
    server_status='playing'
    pygame.mixer.music.unpause()
    print('music resume')

def _saveconfig():
    conf=configparser.ConfigParser()
    conf.read(_conf_file)
    conf['player']['volume']=str(vol)
    conf['player']['list']=playlist_name
    conf['player']['next']=mnext
    conf['player']['index']=str(mindex)
    with open(_conf_file,'w') as f:
        conf.write(f)

def command(opts,udpsvr=None,cltaddr=None):
    '''
    deal commands received from clients to control playing status
    '''
    global isactive, mnext, vol,mfile
    cmd=opts[0]
    response=None
    if cmd=='play':
            play()
            response="playing "+mfile
    elif cmd=='playi':
            try:
                i=init(opt[1])
                if i>=0 and i<len(mlist):
                    mindex=i
                    play()
            except Exception as e:
                print(e)
    elif cmd=='playf':
        try:
            mfile=opts[1]
            if os.path.isabs(mfile)==False:
                for x in mlist:
                    if mfile in os.path.basename(x):
                        mfile=x
            
            mnext='loop'
            play()
            response="playing "+mfile
        except Exception as e:
            print(e)
           
    elif cmd=='stop':
            stop()
    elif cmd=='pause':
            pause()
    elif cmd=='resume':
            unpause()
    elif cmd=='vol':
        try:
            vol=float(opts[1])
            pygame.mixer.music.set_volume(vol)
            response="volume="+str(vol)
            _saveconfig()
        except Exception as e:
            print(e)
    elif cmd=='next':
        try:
            if opts[1] in ('loop','next','random','stop'):
                mnext=opts[1]
                response="next="+mnext
                _saveconfig()
        except Exception as e:
            print(e)
        
    elif cmd=='playlist':
        try:
            loadlist(opts[1])
            response="playlist=%s(%s,%s)"%(playlist_name,len(mlist),playlist_path)
            _saveconfig()
        except Exception as e:
            print(e)
    elif cmd=='info':
        if udpsvr and cltaddr:
            response="Server:Running\nnext=%s,vol=%s,status=%s\nplaylist=%s(%s,%s)\nfile=%s"%(mnext,vol,server_status,playlist_name,len(mlist),playlist_path,mfile)
    elif cmd=='lists':
        conf=configparser.ConfigParser()
        conf.read(_conf_file)
        response=''
        for x in conf['playlists']:
            response=response+'\n'+x
    elif cmd=='list':
        response=''
        for x in mlist:
            response=response+'\n'+x
    elif cmd=='saveconf':
        _saveconfig()
    elif cmd=='exit':
        isactive=False   
        response="server exitted"
    if response:
        udpsvr.sendto(response.encode('utf-8'),cltaddr)
def thcontrol():
    '''
    this function starts a UDP socket which binds at the port 127.0.0.1:6666 
    and receives commands to control the music playback. 
    '''
    global isactive,vol,mport
    udpsvr=socket(AF_INET,SOCK_DGRAM)
    udpsvr.bind(('127.0.0.1',mport))
    print("server started and bind to 127.0.0.1:6666")
    while isactive:
        data,addr=udpsvr.recvfrom(1024)
        cmd=data.decode('utf-8')
        print("msg from %s :%s"%(addr,cmd))
        opts=re.split("=",cmd)        
        try:
            command(opts,udpsvr,addr)    
        except Exception as e:
            print(e)

def sendcmd(cmd):
    global mport
    udpclt=socket(AF_INET,SOCK_DGRAM)
    udpclt.settimeout(1)
    udpclt.sendto(cmd.encode('utf-8'),('127.0.0.1',mport))
    try:
        data,addr=udpclt.recvfrom(1024)
        if data:
            msg=data.decode('utf-8')
            print('Server Response:\n'+msg)
    except Exception as e:
        pass
    
    
def _notify():
    '''
    loop to check the status of playing
    '''
    
    try:
        if pygame.mixer.music.get_busy()==0:
            if mnext!='stop' and server_status=='playing':
                play()        
    except Exception as e:
        print(e)
    if isactive:
        t=threading.Timer(2,_notify)
        t.start()

def main(argv):
    global isactive
    try:
      opts, args = getopt.getopt(argv,"hc:",["server=","test"])  
    except getopt.GetoptError:
        print('-h  //help information')        
        exit(1)
    if len(opts)==0:
        print('hello from mtool by shadow')
        exit(0)
    for opt,arg in opts:
        if opt=='--server' and arg=='start':
            print('starting server')
            _init()
            threading._start_new_thread(thcontrol,())
        elif opt=="-c":
            sendcmd(arg)
            exit(0)
        elif opt=='-h':
            print('--server start  //start server')
            print('-c info|play|pause|resume|stop|list|lists|exit|vol=0.5')
            print('-c playf=filename  //loop to play a music file')
            print('-c next=stop|loop|next|random')
            print('-c playlist=playlistname  //note that the playlistname must be specified in mtool.conf')
            exit(0)
        else:
            print('-h  //help information')
            exit(0)
    
    threading.Timer(2,_notify).start()
    while isactive:
        time.sleep(1)
    print('mtool exit')
    exit(0)




if __name__=='__main__':
    main(sys.argv[1:])
else:
    pass
