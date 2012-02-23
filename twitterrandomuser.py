#!/usr/bin/env python
from tools.tweet import *
import sys
import datetime
import random
from optparse import OptionParser

def random_user(config):
	api = twitter_connect(config)
	users = []
	users.extend(api.followers_ids())
	users.extend(api.friends_ids())
	user_id = random.choice(users)
	user = api.get_user(user_id)
	sys.stdout.write(user.screen_name)

def option_parser():
	parser = OptionParser(usage="Follows random followers of timecube followers on the Moar Time Cube twitter account.")
	parser.add_option("-c", "--config", dest="config", default="moartimecube", help="config name")
	return parser

def main():
	parser = option_parser()
	(options, args) = parser.parse_args()
	config = get_config(options.config)
	random.seed(datetime.datetime.now())
	random_user(config)

if __name__ == "__main__":
	main()

