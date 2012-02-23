#!/usr/bin/env python
from tools.tweet import *
import sys
import datetime
import random
from optparse import OptionParser

def trends(config, num):
	api = twitter_connect(config)
	trends = api.trends_daily()
	for key in trends['trends']:
		for tr in trends['trends'][key]:
			trend = tr['name']
			try:
				print trend
			except Exception:
				#simple way to deal with UTF8 problems
				pass

def option_parser():
	parser = OptionParser(usage="Follows random followers of timecube followers on the Moar Time Cube twitter account.")
	parser.add_option("-n", "--num", dest="num", default="10", help="number of random people to follow")
	parser.add_option("-c", "--config", dest="config", default="moartimecube", help="config name")
	return parser

def main():
	parser = option_parser()
	(options, args) = parser.parse_args()
	config = get_config(options.config)
	num = int(options.num)
	random.seed(datetime.datetime.now())
	trends(config, num)

if __name__ == "__main__":
	main()

