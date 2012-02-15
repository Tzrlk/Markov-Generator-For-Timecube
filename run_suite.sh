#/bin/bash
pushd `dirname "$0" `
#./timecubetrends.py > trending.txt
for i in 1 2 3 4
do
	sleep 30
	selection=$RANDOM
	echo $selection
	if [ "$selection" -gt "30719" ]; then
		# Mention: 1/16
		./markov.py --length 1 --for_twitter --input src.txt --mention `./timecuberandomuser.py` | ./timecubetweet.py
	elif [ "$selection" -gt "26623" ]; then
		# Trending: 2/16
		./markov.py --length 1 --for_twitter --input src.txt --trending trending.txt | ./timecubetweet.py
	else
		# Normal: 13/16
		./markov.py --length 1 --for_twitter --input src.txt | ./timecubetweet.py
	fi
done
sleep 30
./timecubefollow.py -n 24
popd
