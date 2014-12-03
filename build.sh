#! /bin/sh
# business install 
# script name : build.sh

SELF_NAME="build.sh"
VERSION="1.0.1"
SERVER_FILE_NAME="zmon_install_server.tar.gz"
CLIENT_FILE_NAME="zmon_install_ztail.tar.gz"
BUILD_NAME="./output"
CURR_DIR=`pwd`

echo "start building ..."


rm -rf $BUILD_NAME

objs="python ztail redis zcm zpush monflow"
mkdir -p $BUILD_NAME
if [ $? -ne 0 ]; then 
	echo "create dir \"$BUILD_NAME\" failed!"
	exit 1
fi

cp -r $objs $BUILD_NAME
if [ $? -ne 0 ]; then 
	echo "move files to dir \"$BUILD_NAME\" failed!"
	exit 2
fi

cd $BUILD_NAME || exit 1

find ./ -regex "\..+\.svn$" -type d | xargs rm -rf
find ./ -name *.pyc -type f -exec rm -rf {} \;
if [ $? -ne 0 ]; then 
	echo "remove .svn dirs failed!"
	exit 1
fi

sed -i 's/10.38.45.17/10.81.40.205/g' */conf/zmon.yaml 
sed -i 's/DEBUG/INFO/g' */conf/zmon.yaml
#打包server端
tar czf $CLIENT_FILE_NAME python ztail
#打包client端
tar czf $SERVER_FILE_NAME python redis zcm zpush monflow
rm -rf $objs
cd -

echo "$BUILD_NAME has been created at dir $CURR_DIR/output/$SERVER_FILE_NAME $CLIENT_FILE_NAME !"
echo "build succeed!"
exit 0

