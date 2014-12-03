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
cd $this_dir || exit

#mkdir -p status/zcm
mkdir -p log

start() {
        #ulimit -c unlimited
        #setsid ./supervise.zcm status/zcm $pythondir/bin/python bin/zcm.py 1>/dev/null  2>log/zcm.log.wf &
        $pythondir/bin/python bin/zcm.py 1>log/zcm.log.wf 2>&1 &
}

stop() {
        ps -ef|grep "$pythondir/bin/python bin/zcm.py"|grep -v grep|awk '{print $2}'|xargs kill -9 > /dev/null 2>&1
        #echo 'dx' > status/zcm/svcontrol
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
