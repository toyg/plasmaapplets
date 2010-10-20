#!/bin/bash
# the script name should be of the form "install-myappname.sh"
appletsDir=/home/glacava/MySoftware/plasmaapplets

scriptname=`basename $0`
appname=${scriptname:8:${#scriptname}-11}
cd $appletsDir/$appname
zip -r ../${appname}.zip . -x \*.sh \*.mine CMakeLists.txt \*CMakeLists* \*.pot \*.po \*Makefile
cd ..
plasmapkg -i ${appname}.zip

