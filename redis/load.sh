#!/bin/bash

cd `dirname $0` || exit
#mkdir -p status/redis

start() {
	#ulimit -c unlimited
	#setsid ./supervise.redis status/redis setsid bin/redis-server conf/redis.conf </dev/null &>/dev/null &
	bin/redis-server conf/redis.conf </dev/null &>/dev/null &
}

stop() {
	killall supervise.redis redis-server
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
