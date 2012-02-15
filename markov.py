#!/usr/bin/env python
from argparse import ArgumentParser, FileType
from os.path import isfile, abspath
from sys import exit, stdout
from re import split, compile
from random import choice
from operator import itemgetter

# When generating for twitter, this is the minimum number of characters a
# sentence must reach before the algorithm begins selecting smaller words to
# force a sentence ending
TWITTER_ENDING_MIN=100
TWITTER_ENDING_MAX=135

def argparser():
	desc = "Generates pseudo-random sentences using a body of work."
	parser = ArgumentParser(description=desc)
	parser.add_argument("--input", type=FileType("r"), default="-",
						help="Path to the source material to generate from")
	parser.add_argument("--output", default=stdout, type=FileType("w"),
						help="The output file. Defaults to stdout")
	parser.add_argument("--length", default=10, type=int,
						help="The number of sentences to generate")
	parser.add_argument("--size", default=25, type=int,
						help="The length of each sentences to generate")
	parser.add_argument("--seed", type=str,
						help="A word to seed the generator with")
	parser.add_argument("--include_seed", action="store_true", default=False,
						help="Include seed word in generated sentences with")
	parser.add_argument("--for_twitter", action="store_true", default=False,
						help="Generates around 140 characters, but no more")
	parser.add_argument("--trending", type=FileType('r'),
						help="A file containing line-by-line trending topics")
	parser.add_argument("--mention", type=str,
						help="A @username to add to the generated text")

	return parser

def srcparse(src):
	punctuation = compile(r'[*.?!,":;-]')
	word_list = split('\s+', punctuation.sub("", src).lower())
	word_endings = {}

	if len(word_list) < 3:
		print "Source material must contain at least %s words" % group_size
		exit(1)

	for i in range(len(word_list) - 2):
		w1 = word_list[i]
		w2 = word_list[i + 1]
		w3 = word_list[i + 2]
		key = (w1, w2)

		if 0 in [len(w1), len(w2), len(w3)]:
			continue

		# Generate doubles
		if w1 in word_endings:
			word_endings[w1].append(w2)
		else:
			word_endings[w1] = [w2]

		# Generate triples
		if key in word_endings:
			word_endings[key].append(w3)
		else:
			word_endings[key] = [w3]

	return word_list, word_endings

def punctuate(sentence, capitalize=True):
	text = " ".join(sentence)
	if capitalize:
		text = text.capitalize()
	return text + choice([".", "?", "!"])

def twitter_choice(key, endings, text_length):
	"""Filter the word list by length to target a specific character count

	Args:
		key: The key to use for selecting the ending
		endings: A list of selected word endings
		text_length: The current length of the generated text

	Returns:
		The next word to add to the generated output
	"""
	words = endings[key]
	choose_from = []

	# -1 for the space
	remainder = 140 - text_length - 1

	if len(words) == 1 and (remainder - len(words[0]) - 1) <= 140:
		return words[0]

	for word in words:
		# Subtract an additional 1 for the punctuation
		if remainder - len(words[0]) - 1 - 1 <= 140:
			choose_from.append(word)

	if len(choose_from) == 0:
		return False

	return choice(choose_from)

def generate(words, endings, sentences=10, sentence_size=25,
				seed=None, include_seed=False,
				for_twitter=False, mention=None, trending=None):
	"""Generates test using the provided words and endings.

	Args:
		words: A list of words
		endings: A dictionary of word endings created by parsesrc()
		sentences: The number of sentences to generate
		sentence_size: The approximate number of words per sentence
		seed: A word to seed each sentence
		include_seed: Include the seed word as the first word in the sentence
		for_twitter: Generate output for twitter, limiting output at 140 chars
		mention: Adds @mention to the output
		trending: A file which contains a list words to flag for #trending

	Return:
		The generated output
	"""
	# Text length is 1 for the punctuation
	output, sentence, iterations, text_length = [], [], 0, 1
	trends, trending_topics, trending_topic = [], {}, None
	w1, w2 = None, None

	if trending is not None:
		rmhash = compile(r'#')
		for topic in split('\n', trending.read()):
			for w in split('\s+', rmhash.sub("", topic)):
				if len(w) == 0:
					continue
				if w in words:
					trends.append(w)
					try:
						trending_topics[w].append(topic)
					except KeyError:
						trending_topics[w] = [topic]
		if len(trends) > 0:
			spaces = compile(r'\s+')
			seed = choice(trends)
			trending_topic = "#%s" % (spaces.sub("", choice(trending_topics[seed])).lower())
			text_length += len(trending_topic) + 1
			output.append(trending_topic)

	if mention is not None:
		mention = "@{0}".format(mention)
		# Plus 1 for the space
		text_length += len(mention) + 1

	while sentences > 0:
		end_sentence = False
		reset_sentence = False
		skip_append = False

		if w1 is None:
			if seed is not None and seed in words:
				if include_seed:
					w1 = seed
				else:
					w1 = choice(endings[seed])
			else:
				w1 = choice(words)
			w2 = choice(endings[w1])

		# Plus 1 for the space
		text_length += len(w1) + 1
		sentence.append(w1)

		key = (w1, w2)

		iterations += 1

		if key in endings:
			if iterations >= sentence_size and len(endings[key]) == 1:
				end_sentence = True
				key = w1
			else:
				w1 = w2
			if for_twitter and text_length >= TWITTER_ENDING_MIN:
				# For twitter, attempt to pick compact words past 100 chars
				w2 = twitter_choice(key, endings, text_length)
				if w2 == False or text_length + 1 + len(w2) > 140:
					# We must abort and retry; the sentence was too long
					reset_sentence = True
				else:
					text_length += 1 + len(w2)
					if text_length >= TWITTER_ENDING_MAX:
						end_sentence = True
			else:
				w2 = choice(endings[key])
		else:
			end_sentence = True

		if end_sentence:
			if w2 is not None:
				sentence.append(w2)
			output.append(punctuate(sentence, trending_topic is None))
			reset_sentence = True
			sentences -= 1

		if reset_sentence:
			if not end_sentence:
				has_trending = False
			w1, w2, sentence, iterations, text_length = None, None, [], 0, 1
			if mention is not None:
				text_length += len(mention) + 1
			if trending_topic is not None:
				text_length += len(trending_topic) + 1

	if mention is not None:
		output.append(mention)

	return " ".join(output)

def main():
	args = argparser().parse_args()
	words, endings = srcparse(args.input.read())
	text = generate(words, endings, args.length, args.size,
					args.seed, args.include_seed,
					args.for_twitter, args.mention, args.trending)
	args.output.write(text + "\n")

if __name__ == "__main__":
	main()

