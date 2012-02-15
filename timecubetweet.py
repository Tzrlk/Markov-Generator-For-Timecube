#!/usr/bin/env python
from tools.tweet import *
import sys
import datetime
import random
from optparse import OptionParser

def post_tweet(config, doc):
	api = twitter_connect(config)
	api.update_status(doc)

def tweet(config):
	doc = "".join(sys.stdin.readlines())
	if len(doc) > 140:
		return
	elif len(doc) <= 130:
		val = random.random()
		if val < 0.02:
			doc = "@TimeCube " + doc
		elif val > 0.98:
			doc = doc + " @TimeCube"
	print doc.strip()
	post_tweet(config, doc.strip())

def option_parser():
	parser = OptionParser(usage="Posts generated tweets to Moar Time Cube twitter account.")
	return parser

def main():
	parser = option_parser()
	(options, args) = parser.parse_args()
	config = get_config()
	random.seed(datetime.datetime.now())
	tweet(config)

if __name__ == "__main__":
	main()
