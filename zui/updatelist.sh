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
dirPath='data/updateflag'
while true;do
    sleep 0.1
    products=$(ls $dirPath)
    if [ $? -ne 0 ];then
        continue
    fi
    for product in $products;do
        begin=$(date '+%s')
        echo "$begin begin to update produt: $product" >> log/updatelist.log
        $pythondir/bin/python bin/zlist.py $product
        now=$(date '+%s')
        used=$(($now-$begin))
        echo "finish to update produt: $product use $used second" >> log/updatelist.log
        if [ $? -eq 0 ];then
            rm -f $dirPath/$product
        else
            gsmsend-script 15210972802@"update $product list faile!"
        fi
    done
done
