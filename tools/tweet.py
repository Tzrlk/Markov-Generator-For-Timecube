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

def get_config(name):
	if os.path.exists('%s.yaml' % name):
		return yaml.load(file('%s.yaml' % name, 'r'))['twitter']
	elif os.path.exists(os.path.expanduser('~/.%s' % name)):
		return yaml.load(file(os.path.expanduser('~/.%s' % name), 'r'))['twitter']
	elif os.path.exists('/etc/%s.yaml' % name):
		return yaml.load(file('/etc/%s.yaml' % name, 'r'))['twitter']
	else:
		raise Exception('No config file')

