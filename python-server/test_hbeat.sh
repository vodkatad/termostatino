#!/bin/bash
i="0"
# we send 3 good heartbeat than pretend to be dead
while [ $i -lt 10 ]; do
	curl -v localhost:8000/TermostatinoHandler;
	echo beat;
	sleep 10;
	i=$[$i+1];
done;
sleep 80;
# and alive again
while true; do
	curl -v localhost:8000/TermostatinoHandler;
	echo rebeat;
	sleep 10;
done;
