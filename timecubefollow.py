#!/usr/bin/env python
from tools.tweet import *
import sys
import datetime
import random
from optparse import OptionParser

def follow(config, num):
	api = twitter_connect(config)
	followers = api.followers()
	tries = 0
	follower = select_follower(followers)
	ffs = follower.followers()
	print "Follower: %s" % follower.name
	while num > 0:
		print num
		tries = tries + 1
		user = select_follower(ffs)
		print "Victim: %s" % user.name
		num = do_follow(api, user, num)
		if tries == 10:
			follower = select_follower(followers)
			print "Follower: %s" % follower.name
			ffs = follower.followers()
			tries = 0


def select_follower(followers):
	return random.sample(followers, 1)[0]

def do_follow(api, user, num):
	if not user.following:
		num = num - 1
		api.create_friendship(user.screen_name)
	return num

def option_parser():
	parser = OptionParser(usage="Follows random followers of timecube followers on the Moar Time Cube twitter account.")
	parser.add_option("-n", "--num", dest="num", default="10", help="number of random people to follow")
	return parser

def main():
	parser = option_parser()
	(options, args) = parser.parse_args()
	config = get_config()
	num = int(options.num)
	random.seed(datetime.datetime.now())
	follow(config, num)

if __name__ == "__main__":
	main()

