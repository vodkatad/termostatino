#!/bin/bash
i="0"
# we send 3 good heartbeat than pretend to be dead
while [ $i -lt 361 ]; do
	curl -v -d 'temp=45' localhost:8000/TermostatinoHandler;
	echo beat;
	i=$[$i+1];
done;
# We get two mail for 45
curl -v -d 'temp=25' localhost:8000/TermostatinoHandler;
curl -v -d 'temp=55' localhost:8000/TermostatinoHandler;
# a mail for 55
curl -v -d 'temp=25' localhost:8000/TermostatinoHandler;
sleep 70;
# a missed heartbeat
while [ $i -lt 370 ]; do
	curl -v -d 'temp=25' localhost:8000/TermostatinoHandler;
	echo rebeat;
	i=$[$i+1];
	sleep 10;
done;
curl -v -d 'temp=65' localhost:8000/TermostatinoHandler;
#and a 65 mail
