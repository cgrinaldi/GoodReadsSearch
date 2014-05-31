# Importing the necessary libraries
from rauth.service import OAuth1Service, OAuth1Session
import oauth2 as oauth
import xml.etree.ElementTree as ET
import urllib
import time

# API Information
CONSUMER_KEY = 'chQHQQNMvcfswX9dEu3IXA'
CONSUMER_SECRET = 'wCUQn3dpg9UGB1a2ZPXPVzz0edpeVxYaNDAiaVvU'
ACCESS_TOKEN = '7aemoVRKkcygkdgoYsYvJw'
ACCESS_TOKEN_SECRET = 'AN8P4sJMSlPpWI1C2HqfjNnLXnZlsjPN06V7trw'
usr_id = '2318715'

#########################################################################
## FUNCTIONS
#########################################################################
def pull_shelf(shelf):
	"""Pulls the books off of GoodReads to_search shelf and outputs a dictionary
	that maps the isbn to goodreads id."""

	new_session = OAuth1Session(
    consumer_key = CONSUMER_KEY,
    consumer_secret = CONSUMER_SECRET,
    access_token = ACCESS_TOKEN,
    access_token_secret = ACCESS_TOKEN_SECRET)

    # Getting GoodReads XML for to-read shelf
	url = 'http://www.goodreads.com/review/list/%s.xml?v=2&key=%s&per_page=200&shelf=%s' % (usr_id, CONSUMER_KEY, shelf)
	response = new_session.get(url)
	page = response.text
	time.sleep(1.1)

	# Parsing the XML
	root = ET.fromstring(page.encode('UTF-8'))
	books = root[1]

	# Storying the ISBNs and GoodReads ID
	books_info = []
	for book in books:
		# isbn, goodreadsid, author, book
		books_info.append((book[1][1].text, book[1][0].text, book[1][-2][0][1].text, book[1][4].text))

	return books_info

error_books = []
def book_at_library(author, book, isbn):
	"""Given an isbn, search the Montgomery County library and
	return True if present."""

	lib_url = 'http://mdpl.ent.sirsi.net/client/catalog/search/results?qu='
	lib_url += author + '+' + book
	lib_url += '&te=ILS' 

	try:
		page = urllib.urlopen(lib_url)
		page_contents = page.read()
	except:
		error_books.append((author, book))
		return False

	if page_contents.find('This search returned no results.') == -1:
		return True
	else:
		# Try looking for the ISBN
		if isbn == None: return False
		lib_url = 'http://mdpl.ent.sirsi.net/client/catalog/search/results?qu='
		lib_url += isbn
		lib_url += '&te=ILS&rt=false%7C%7C%7CISBN%7C%7C%7CISBN' 

		page = urllib.urlopen(lib_url)
		page_contents = page.read()

		if page_contents.find('This search returned no results.') == -1:
			return True
		else:
			return False

	time.sleep(1)

def move_book(title, book_id, shelf, remove=False):
	url = 'http://www.goodreads.com'
	consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	token = oauth.Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	client = oauth.Client(consumer, token)

	if not remove:
		body = urllib.urlencode({'name': shelf, 'book_id': book_id})
	else:
		body = urllib.urlencode({'name': shelf, 'book_id': book_id, 'a':'remove'})
	
	headers = {'content-type': 'application/x-www-form-urlencoded'}
	response, content = client.request('%s/shelf/add_to_shelf.xml' % url,
										'POST', body, headers)

	if not remove:
		if response['status'] == '201' or response['status'] == '200':
			print "%s moved to %s" % (title, shelf)
		else:
			print "ERROR: %s" % title

	time.sleep(1.1)

def find_related_books(isbn):
	"""Given an isbn, query GoodReads to get Title and Author.
	Search GoodReads, and get related isbns and GoodRead ids."""
	
	# Create search query
	url = 'https://www.goodreads.com/search.xml?key=%s' % CONSUMER_KEY
	url += '&q=%s' % isbn


	# Call and parse xml
	page = urllib.urlopen(url)
	page_contents = page.read()
	root = ET.fromstring(page_contents)
	search_results = root[1]
	author = search_results[-1][0][-1][2][1].text
	title = search_results[-1][0][-1][1].text

	# Cleaning title and author in order to query website
	clean_author = ""
	for c in author:
		clean_author += _map_chr(c)

	clean_title = ""
	for c in title:
		clean_title += _map_chr(c)

	# Search GoodReads for Author/Title combination
	url = 'https://www.goodreads.com/search.xml?key=%s' % CONSUMER_KEY
	url += '&q=%s' % (clean_author + "+" + clean_title) 

	page = urllib.urlopen(url)
	page_contents = page.read()

	time.sleep(1.1)

	root = ET.fromstring(page_contents)
	results = root[1][-1]

	for result in results:
		book_id = result[-1][0].text
		move_book(book_id, 'to_search')

def convert_word(word):
	new_word = ""
	for c in word:
		new_word += _map_chr(c)
	return new_word

def _map_chr(c):
	chr_mapping = {" ": '+',
					':': '%3A',
					"'": '%27'}
	if c in chr_mapping:
		return chr_mapping[c]
	return c

#########################################################################
## SCRIPT
#########################################################################

def script():
	# Pull to search shelf
	books_info = pull_shelf('to_search')

	# Finding the books at library
	at_lib = []
	not_lib = []
	for isbn, book_id, author, book in books_info:
		cleaned_author = convert_word(author)
		cleaned_book = convert_word(book)

		if book_at_library(author, book, isbn):
			at_lib.append((isbn, book_id, author, book))
		else:
			not_lib.append((isbn, book_id, author, book))

	# Moving the books at the library to library shelf
	for _, book_id, _, book in at_lib:
		move_book(book, book_id, 'to_library')
		move_book(book, book_id, 'to_search', remove=True)

	# Removing the books not at the library
	for _, book_id, _, book in not_lib:
		move_book(book, book_id, 'not_library')
		move_book(book, book_id, 'to_search', remove=True)

	print "-" * 15
	print "Search found %d books at the library." % len(at_lib) 
	print "Search could not find %d books at the library." % len(not_lib)
	return at_lib, not_lib

script()







