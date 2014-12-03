#!/bin/bash

#get Current Dir
this_dir=$PWD
dirname $0|grep "^/" >/dev/null
if [ $? -eq 0 ];then
        this_dir=$(dirname $0)
else
        dirname $0|grep "^\." >/dev/null
        retval=$?
        if [ $retval -eq 0 ];then
                this_dir=$(dirname $0|sed "s#^.#$this_dir#")
        else
                this_dir=$(dirname $0|sed "s#^#$this_dir/#")
        fi
fi

#get Python Dir
pythondir=$(dirname $this_dir)/python

#set PYTHONPATH
#export PYTHONPATH=$pythondir/lib/zeromq/lib:$PYTHONPATH
#export PYTHONPATH=$pythondir/lib/redis:$PYTHONPATH
#export PYTHONPATH=$pythondir/lib/rms:$PYTHONPATH
#export PYTHONPATH=$pythondir/lib:$PYTHONPATH
export PYTHONPATH=$pythondir/lib/python2.7/site-packages/base:$PYTHONPATH
#export LD_LIBRARY_PATH=$pythondir/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$pythondir/lib/python2.7/site-packages/zeromq/lib/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

#redisPath=$pythondir/lib/redis
#webPath=$pythondir/lib/python2.7/site-packages
#mysqlPath=$pythondir/lib/python2.7/site-packages/MySQL_python-1.2.4b4-py2.7-linux-x86_64.egg

cd $this_dir || exit

#mkdir -p status/uwsgi.zui
mkdir -p log
#ulimit -c unlimited

start() {
	#setsid ./supervise.zui status/uwsgi.zui setsid bin/uwsgi.zui -s :6666 --buffer-size 65535 --harakiri 600 --processes 8 --limit-as 1024 --catch-exceptions --pp bin --pp $redisPath --pp $webPath --pp $mysqlPath -w zui -M -t 20 -R 10000 --vacuum --logdate --logto log/uwsgi.log &
	bin/uwsgi -s :6666 --buffer-size 65535 --harakiri 600 --processes 8 --limit-as 1024 --catch-exceptions --pp bin -w zui -M -t 20 -R 10000 --vacuum --logdate --logto log/uwsgi.log &
}

stop() {
    killall -9 uwsgi
    #killall -9 supervise.zui uwsgi.zui
    #[ -f status/uwsgi.zui/svcontrol ] && echo 'dx' > status/uwsgi.zui/svcontrol 
}

case "$1" in
	start)
                stop
		start
		echo "Done!"
		;;
	stop)
		stop
		echo "Done!"
		;;
	*)
		echo "Usage: $0 {start|stop}"
		;;
esac
