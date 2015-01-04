#!/bin/bash
#==========================
# bash - find path to script
#    abspath=$(cd ${0%/*} && echo $PWD/${0##*/})
# to get the path only - not the script name - add
#    path_only=`dirname "$abspath"`
#==========================
## décommenter pour créer un lanceur
#~ here=`dirname "$(cd ${0%/*} && echo $PWD/${0##*/})"`
#~ cd $here
