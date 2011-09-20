#!/bin/sh

killall -9 java

for i in 1 2 3 4 5 6 7 8 9
do
  dropdb nuxeo$i
done

for pid in `ps auxxxw | grep nginx | egrep -v '(grep|kill)' | cut -d' ' -f2`
do
  kill $pid
done

\rm -rf ~/nuxeocloud/instances/*
\rm -rf ~/nuxeocloud/nuxeocloud.db

supervisorctl -c /Users/fermigier/nuxeocloud//supervisor.conf shutdown
