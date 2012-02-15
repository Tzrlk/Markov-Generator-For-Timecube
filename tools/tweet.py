import tweepy
import yaml
import os
import sys

def twitter_connect(config):
	auth = twitter_auth(config)
	return tweepy.API(auth)

def twitter_auth(config):
	auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
	auth.set_access_token(config['access_token'], config['access_token_secret'])
	return auth

def get_config():
	if os.path.exists('moartimecube.yaml'):
		return yaml.load(file('moartimecube.yaml', 'r'))['moartimecube']
	elif os.path.exists(os.path.expanduser('~/.moartimecube')):
		return yaml.load(file(os.path.expanduser('~/.moartimecube'), 'r'))['moartimecube']
	elif os.path.exists('/etc/moartimecube.yaml'):
		return yaml.load(file('/etc/moartimecube.yaml', 'r'))['moartimecube']
	else:
		raise Exception('No config file')

