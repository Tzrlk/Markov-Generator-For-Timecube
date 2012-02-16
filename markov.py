#!/usr/bin/env python
from argparse import ArgumentParser, FileType
from os.path import isfile, abspath
from sys import exit, stdout
from re import split, compile
from random import choice
from operator import itemgetter
from nltk.data import load
from nltk import word_tokenize

# When generating text, attempt to end a sentence when the length of the
# sentence is within this number of the specified target size
SENTENCE_ENDING_MIN=5

# The minimum number of words for a full sentence
SENTENCE_LENGTH_MIN=8

# The total number of sentences to unsuccessfully generate before abandoning
HARD_STOP = 50

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
	tokenizer = load("tokenizers/punkt/english.pickle")
	sentences = tokenizer.tokenize(src.strip().lower())
	bs = compile(r'\d*:\d')
	rm = compile(r'[*.?!,\'":;\(\)<>]')
	sp = compile(r'[\-\+]')

	starts, joins, ends = [], {}, []

	for sentence in sentences:
		# Format the sentence
		wlist = word_tokenize(bs.sub(" ", sp.sub(" ", rm.sub("",
			sentence.replace("\n", " ")))))

		if len(wlist) < 3:
			# Ignore sentences without triples in the corpus
			continue

		# Add the sentence starting word
		starts.append(wlist[0])

		# Inverse the list so we can build from the ending
		wlist.reverse()

		for i in range(len(wlist) - 2):
			w1 = wlist[i]
			w2 = wlist[i + 1]
			w3 = wlist[i + 2]

			# Handle zero-length breaks in the corpus.
			if 0 in [len(w1), len(w2), len(w3)]:
				continue

			# Generate a list of words which can start a sentence properly
			if i == 0:
				ends.append(w1)

			# Store doubles
			try:
				joins[w1].append(w2)
			except KeyError:
				joins[w1] = [w2]

			# Store triples
			key = (w1, w2)
			try:
				joins[key].append(w3)
			except KeyError:
				joins[key] = [w3]

	return starts, joins, ends

def punctuate(sentence, capitalize=True):
	text = " ".join(sentence)
	if capitalize:
		text = text.capitalize()
	return text + "."

def generate(starts, joins, ends,
				sentences=10, size=25,
				seed=None, include_seed=False,
				for_twitter=False, mention=None, trending=None):
	"""Generates test using the provided words and endings.

	Args:
		starts: A list of words that starts sentences
		joins: A dictionary of word endings (going backwards)
		ends: A list of words that ends sentences
		sentences: The number of sentences to generate
		size: The approximate number of words per sentence
		seed: A word to seed each sentence
		include_seed: Include the seed word as the first word in the sentence
		for_twitter: Generate output for twitter, limiting output at 140 chars
		mention: Adds @mention to the output
		trending: A file which contains a list words to flag for #trending

	Return:
		The generated output
	"""

	output, hard_stop_iterations, trending_topic = [], 0, None

	if trending is not None:
		rmformat = compile(r'#|\s+')
		topic = choice(split('\n', trending.read()))
		trending_topic = "#{}".format(rmformat.sub("", topic))

	while sentences > 0:
		if hard_stop_iterations >= HARD_STOP:
			break

		# Build the sentence in reverse, starting at the ending word
		sentence = []

		# We add the mention first because the sentence

		if seed in ends:
			if include_seed:
				w1 = seed
			else:
				w1 = choice(joins[seed])
		else:
			w1 = choice(ends)
		w2 = choice(joins[w1])

		while True:
			sentence.append(w1)
			key = (w1, w2)
			if key in joins:
				w1, w2 = w2, choice(joins[key])
			else:
				break
			if w2 in starts and (len(sentence) + SENTENCE_ENDING_MIN) >= size:
				sentence.append(w2)
				break

		if len(sentence) >= SENTENCE_LENGTH_MIN:
			if trending_topic is not None:
				sentence.append(trending_topic)
			sentence.reverse()
			formatted_sentence = punctuate(sentence)
			if mention is not None:
				formatted_sentence += " @{}".format(mention)
			if for_twitter:
				if len(formatted_sentence) > 140:
					break
			output.append(formatted_sentence)
			sentences -= 1

		hard_stop_iterations += 1

	return " ".join(output)

def main():
	args = argparser().parse_args()
	starts, joins, ends = srcparse(args.input.read())
	text = generate(starts, joins, ends,
					args.length, args.size,
					args.seed, args.include_seed,
					args.for_twitter, args.mention, args.trending)
	args.output.write(text + "\n")

if __name__ == "__main__":
	main()

