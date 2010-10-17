#!/bin/bash
# the script name should be of the form "remove-myappname.sh"
scriptname=`basename $0`
appname=${scriptname:7:${#scriptname}-10}

plasmapkg -r $appname
