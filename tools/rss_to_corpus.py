#!/usr/bin/env python
from argparse import ArgumentParser, FileType
from sys import exit, stdout
from feedparser import parse
from urlparse import urlparse, urlunparse, parse_qsl
from urllib import urlencode
from nltk import clean_html
from re import sub
from HTMLParser import HTMLParser

from pprint import pprint as pp

# The index in a urlparse()'d result of the query params
QUERY_INDEX = 4

def argparser():
	desc = "Uses an RSS feed to generate a corpus"
	parser = ArgumentParser(description=desc)
	parser.add_argument("url", metavar="URL",
						help="URL of the feed")
	parser.add_argument("--output", default=stdout, type=FileType("w"),
						help="The output file. Defaults to stdout")
	parser.add_argument("--paging_name", default="paged", type=str,
						help="URL parameter for walking through pages")
	parser.add_argument("--starting_page", default=1, type=int,
						help="A word to seed the generator with")

	return parser

def update_url_params(url, update):
	parsed_url = list(urlparse(url))
	params = dict(parse_qsl(parsed_url[QUERY_INDEX]))
	params.update(update)
	parsed_url[QUERY_INDEX] = urlencode(params)
	return urlunparse(parsed_url)

def encode_utf8_to_iso88591(utf8_text):
    """From: http://www.jamesmurty.com/2011/12/30/python-code-utf8-to-latin1/
    Encode and return the given UTF-8 text as ISO-8859-1 (latin1) with
    unsupported characters replaced by '?', except for common special
    characters like smart quotes and symbols that we handle as well as we can.
    For example, the copyright symbol => '(c)' etc.

    If the given value is not a string it is returned unchanged.

    References:
    en.wikipedia.org/wiki/Quotation_mark_glyphs#Quotation_marks_in_Unicode
    en.wikipedia.org/wiki/Copyright_symbol
    en.wikipedia.org/wiki/Registered_trademark_symbol
    en.wikipedia.org/wiki/Sound_recording_copyright_symbol
    en.wikipedia.org/wiki/Service_mark_symbol
    en.wikipedia.org/wiki/Trademark_symbol
    """
    if not isinstance(utf8_text, basestring):
        return utf8_text
    # Replace "smart" and other single-quote like things
    utf8_text = sub(
        u'[\u02bc\u2018\u2019\u201a\u201b\u2039\u203a\u300c\u300d]',
        "'", utf8_text)
    # Replace "smart" and other double-quote like things
    utf8_text = sub(
        u'[\u00ab\u00bb\u201c\u201d\u201e\u201f\u300e\u300f]',
        '"', utf8_text)
    # Replace copyright symbol
    utf8_text = sub(u'[\u00a9\u24b8\u24d2]', '(c)', utf8_text)
    # Replace registered trademark symbol
    utf8_text = sub(u'[\u00ae\u24c7]', '(r)', utf8_text)
    # Replace sound recording copyright symbol
    utf8_text = sub(u'[\u2117\u24c5\u24df]', '(p)', utf8_text)
    # Replace service mark symbol
    utf8_text = sub(u'[\u2120]', '(sm)', utf8_text)
    # Replace trademark symbol
    utf8_text = sub(u'[\u2122]', '(tm)', utf8_text)
    # Replace/clobber any remaining UTF-8 characters that aren't in ISO-8859-1
    return utf8_text.encode('ISO-8859-1', 'ignore')

def fetch_posts(url, paging_name="paged", starting_page=1):
	posts = []
	page_update = {}
	current_page = starting_page
	parser = HTMLParser()

	while True:
		page_update[paging_name] = current_page
		url = update_url_params(url, page_update)
		feed = parse(url)
		if len(feed["entries"]) == 0:
			break
		for e in feed["entries"]:
			text = parser.unescape(clean_html(e["content"][0]["value"]))
			posts.append(encode_utf8_to_iso88591(text))
		current_page += 1

	return posts

def main():
	args = argparser().parse_args()
	posts = fetch_posts(args.url, args.paging_name, args.starting_page)
	args.output.write("\n".join(posts))

if __name__ == "__main__":
	main()
