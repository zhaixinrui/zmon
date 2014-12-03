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

cd $this_dir || exit
mkdir -p logs

start() {
    ./sbin/nginx -p $this_dir/
}

stop() {
	./sbin/nginx -s stop
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
