#!/usr/bin/env python
from tools.tweet import *
import sys
import datetime
import random
from optparse import OptionParser

def unfollow(config, num):
	api = twitter_connect(config)
	friend_ids = api.friends_ids()
	follower_ids = api.followers_ids()
	itercnt = 0
	total = num * 10
	while num > 0:
		fid = random.choice(friend_ids)
		if fid not in follower_ids:
			user = api.get_user(fid)
			ratio = 0.0
			if user.friends_count > 0:
				ratio = float(user.followers_count) / float(user.friends_count)
			if user.followers_count > 2000:
				print "Popular: %s" % fid
			elif ratio < 0.35:
				num -= 1
				api.destroy_friendship(fid)
				print "Removing: %s" % fid
			else:
				print "Descriminating: %s" % fid
		else:
			print "Keeping: %s" % fid
		itercnt += 1
		if itercnt > total:
			return

def follow_followers(api, followers):
	for follower in followers:
		do_follow(api, follower)

def select_follower(followers):
	return random.sample(followers, 1)[0]

def do_unfollow(api, user, num=0):
	if not user.following:
		num = num - 1
		try:
			api.create_friendship(user.screen_name)
			print "Victim: %s" % user.name
		except:
			# Something failed in the follow, accept that and move on
			pass
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
	unfollow(config, num)

if __name__ == "__main__":
	main()

