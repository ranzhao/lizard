#!/bin/awk -f
BEGIN {
    printf "begin lizard parsing..."
}
{
    #param = "--until='2016-08-19' --pretty=format:'%h' -1"
    #cmd = sprintf("cd %s; git pull; return=`git log %s`; git reset --hard $return", $3, param)
    #system(cmd)

    cmd = sprintf("cd %s; pwd; git pull; cd -", $3)
    system(cmd)
    #cmd = sprintf("lizard -l %s -C 10 -D 20 -Edependency -x \"*/test/*\" -json ../chm/web/data/health/%s-all.json -csv ../chm/web/data/health/%s-trend.csv -Ecpd --cpd_file ../chm/web/data/health/%s-cpd.json -Eactivitygraph --activity_file ../chm/web/data/health/%s-active.csv %s", $1, $2, $2, $2, $2, $3)
    cmd = sprintf("lizard -l %s -C 10 -D 20 -Edependency -x \"*/test/*\" -json ../chm/web/data/health/%s-all.json -Ecpd --cpd_file ../chm/web/data/health/%s-cpd.json -Eactivitygraph --activity_file ../chm/web/data/health/%s-active.csv %s", $1, $2, $2, $2, $3)
    for (i = 4; i <= NF; i++) cmd = cmd sprintf(" -x %s", $i)
    system(cmd)
}
END {
    printf "finish lizard parsing"
}
