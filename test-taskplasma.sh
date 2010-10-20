#!/bin/bash
# the script name should be of the form "test-myappname.sh"
appletsDir=/home/glacava/MySoftware/plasmaapplets

scriptname=`basename $0`
appname=${scriptname:5:${#scriptname}-8}
cd $appletsDir/$appname
zip -r ../${appname}.zip . -x \*.sh \*.mine CMakeLists.txt \*CMakeLists* \*.pot \*.po \*Makefile
cd ..
plasmapkg -i ${appname}.zip
plasmoidviewer ${appname}
plasmapkg -r ${appname}
