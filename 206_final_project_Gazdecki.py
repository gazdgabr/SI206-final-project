"""
Gabriella Gazdecki
SI 206 W17 
Final Project
Option 2 - API Mashup: Twitter & OMDB
"""
# Put all import statements you need here.
import json
import requests
import re
import tweepy
import twitter_info
import collections 
import sqlite3
import unittest
import itertools
import random
import itertools

## Tweepy setup code borrowed from code given by Professor Cohen this semester.
##### TWEEPY SETUP CODE:

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Caching pattern:

cache_filename = "206_final_project_cache.json"

try:
	cache_file = open(cache_filename,'r')
	cache_stuff = cache_file.read()
	cache_file.close()
	cache_dictionary = json.loads(cache_stuff)

except:
	cache_dictionary = {}


# Write a function called get_twitter_user that goes to Twitter, gets data about a Twitter user, and dumps it in the cache:

def get_twitter_user(desiredUser):

	if desiredUser + "_user" in cache_dictionary:
		User = cache_dictionary[desiredUser + "_user"]

	else:
		User = api.get_user(desiredUser)
		cache_dictionary[desiredUser + "_user"] = User

		f = open(cache_filename,'w')
		f.write(json.dumps(cache_dictionary))
		f.close()
	return User


# Write a function called get_twitter_term that goes to Twitter, gets tweets associated with a search term, and dumps them in the cache:

def get_twitter_term(keyPhrase):
	if keyPhrase + "_tweets"  in cache_dictionary:
		results = cache_dictionary[keyPhrase + "_tweets"]
	else:
		results = api.search(q=keyPhrase, count=30)
		results = results["statuses"]
		cache_dictionary[keyPhrase + "_tweets"] = results
		
		f = open(cache_filename,'w')
		f.write(json.dumps(cache_dictionary))
		f.close()
	return results


# Write a function called get_OMDB_info that goes to the OMDB API, gets data about a specified movie, and dumps the result in the cache:

def get_OMDB_info(movie):
	if movie in cache_dictionary:
		results = cache_dictionary[movie]

	else:
		baseurl = "http://www.omdbapi.com/?t="
		request = baseurl + movie

		results = requests.get(request)
		results = json.loads(results.text)

		cache_dictionary[movie] = results

		f = open(cache_filename,'w')
		f.write(json.dumps(cache_dictionary))
		f.close()

	return results


# Create a class to handle Twitter users, call it twitterUsers. This will contain variables to store the user's ID, screen name, favorites count, and followers count. 

class twitterUsers(object):

	# Define a constructor which takes in a dictionary representing a Twitter user, and stores the pertinent data in the proper variables:
	def __init__(self, UserDiction):
		self.user_id = UserDiction["id"]
		self.screen_name = UserDiction["screen_name"]
		self.favourites_count = UserDiction["favourites_count"]
		self.followers_count = UserDiction["followers_count"]

	# Define a method that returns a the ID of the user:
	def __str__(self):
		return self.user_id

	# Define a method that returns a list in this format: [screenname, favorites count, followers count]:
	def infoList(self):
		return [self.screen_name, self.favourites_count, self.followers_count]



# Create a class to handle the movie data; call it Movie. This will contain variables to store its title, its director, its IMDB rating, a list of actors, and the number of languages the movie is in:
class Movie(object):

	# Define a constructor which takes in a dictionary representing a movie, and stores the pertinent data in the proper variables:
	def __init__(self, MovieDiction):
		self.title= MovieDiction["Title"]
		self.director = MovieDiction["Director"]
		self.IMDB = MovieDiction["imdbRating"]
		self.actors = MovieDiction["Actors"].split(", ")
		self.numLang = len(MovieDiction["Language"].split(", "))
		self.id = int((re.findall("tt([0-9]*)", MovieDiction["imdbID"]))[0])

	# Define a _str_ method that returns the name of the movie:
	def __str__(self):
		return self.title

	# Define a method called infoList which returns a list in this format: [director, imdb rating, list of actors, number of languages]:
	def infoList(self):
		return [self.director, self.IMDB, self.actors, self.numLang, self.id]

class Tweet(object):

	def __init__(self, tweetDiction, Movie="unrelated"):
		self.tweet_text = tweetDiction["text"].encode('utf-8')
		self.tweet_id = tweetDiction["id"]
		self.user = tweetDiction["user"]["id"]
		self.movie = Movie
		self.favorites = tweetDiction["favorite_count"]
		self.retweets = tweetDiction["retweet_count"]

	def __str__(self):
		return self.tweet_text

	def priKey(self):
		return self.tweet_id

	def infoList(self):
		return [self.tweet_text, self.user, self.movie, self.favorites, self.retweets]

# Create a list containing the names of three (or more) movies:
threeMoviez = ["Power Rangers", "Pulp Fiction", "The Fate of the Furious", "The Boss Baby", "Hidden Figures",
				 "Smurfs: The Lost Village", "Phoenix Forgotten"]

# Invoke the get_OMDB_info() function on all three of these movies:
threeMovieDictions = []
for movie in threeMoviez:
	threeMovieDictions.append(get_OMDB_info(movie))

# Using threeMovieDiction, create a Movie instance class for each of the three movies:
threeMovies = []
for movie in threeMovieDictions:
	threeMovies.append(Movie(movie))

# Invoke the get_twitter_term() function for each of those three movies, store the resulting dictionaries in a list of tuples:
MovieTweets = [(movie, get_twitter_term(movie)) for movie in threeMoviez]

# Gather data about each user in the neighborhood of these tweets.
	# Iterate through all of the tweets in MovieTweets and store the screenname of each tweets author, and also the screen name of each mentioned user. Store all of these screen names in a list called neighborhood:

#Put all the retrieved tweets into a single list, called TweetList:
TweetList = []
for List in MovieTweets:
	TweetList = TweetList + List[1]

# Search this list for all of the mentioned users, storing the resulting list of all user strings into the variable neighborhood:
neighborhood = []
for maBoi in TweetList:
	batch = re.findall("@([0-9A-Z_a-z]+)", maBoi.__str__())
	neighborhood = neighborhood + batch

# Make all the gathered tweets into tweet objects. Store resulting list of tweet objects in variable YaTweets:
YaTweets = []
for movie in MovieTweets:
	for maTweet in movie[1]:
		YaTweets.append(Tweet(maTweet, movie[0]))

# Make a new list of user strings where all users are lowercase:
lowerBoiz = []
for aBoi in neighborhood:
	lowerBoiz.append(aBoi.lower())

# Remove duplicate user strings:
neighborhood = list(set(lowerBoiz))

# Iterate across the neighborhood list and create an instance of TwitterUsers for each screenName in this list.
# Convert all those user strings into user objects.
# The try/except prevents run time errors due to suspended or non-existent users.
maHood = []
for maBoi in neighborhood:
	try:
		maBoi = get_twitter_user(maBoi)
		maBoi = twitterUsers(maBoi)
		maHood.append(maBoi)
	except:
		pass
	

# Create a database file called finalproject.db. It should have three tables: Tweets, Users, and Movies. Each table should be laid out as follows:

# Tweets, with these columns:
	# tweet_text - the text in the tweet
	# tweet_id - the INTEGER PRIMARY KEY, with the string ID of the tweet from Twitter
	# user - the ID string that represents the user - references the Users table
	# movie - the string of the movie search the tweet came from; it will reference the Movies table
	# favorites - integer that represents the number of favorites that the tweet has
	# retweets - integer that represents the number of retweets that the tweet has

# Users, with these columns:
	# user_id - the INTEGER PRIMARY KEY, with the string ID of the Twitter user
	# screen_name - a string with the Twitter handle of the person who tweeted this tweet
	# user_favs - integer that represents the number of favorites the user has
	# followers - integer that represents the number of followers the user has

# Movies, with these columns:
	# movie_id - INTEGER PRIMARY KEY, with the string ID of the movie in the OMDB
	# title - string title of the movie
	# director - string name of the movie's director
	# languages - integer that represents the number of languages the movie is in
	# rating - string that represents the movie's IMDB rating
	# top_actor - string name of the top billed actor in the movie

conn = sqlite3.connect('finalproject.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('DROP TABLE IF EXISTS Users')
cur.execute('DROP TABLE IF EXISTS Movies')

statement = 'CREATE TABLE IF NOT EXISTS '
statement += 'Tweets (tweet_text TEXT, tweet_id INTEGER PRIMARY KEY, user TEXT, movie TEXT, favorites INTEGER, retweets INTEGER)'
cur.execute(statement)

statement = 'CREATE TABLE IF NOT EXISTS '
statement += 'Users (user_id INTEGER PRIMARY KEY, screen_name TEXT, user_favs INTEGER, followers INTEGER)'
cur.execute(statement)

statement = 'CREATE TABLE IF NOT EXISTS '
statement += 'Movies (movie_id INTEGER PRIMARY KEY, title TEXT, director TEXT, languages INTEGER, rating TEXT, top_actor TEXT)'
cur.execute(statement)


# The following is adapted from Project 3
# Add data to Users table:
element_list = []
for maBoi in maHood:
		stuff = maBoi.infoList()

		user_id_item = maBoi.__str__()
		screen_name_item = stuff[0]
		user_favs_item = stuff[1]
		followers_item = stuff[2]
		element_list.append((user_id_item, screen_name_item, user_favs_item, followers_item))

statement = 'INSERT INTO Users VALUES (?, ?, ?, ?)'    
for element in element_list:
	try:
		cur.execute(statement, element)
	except:
		pass

# Add data to Tweets table:
element_list = []
for maBoi in YaTweets:
		stuff = maBoi.infoList()

		tweet_id = int(maBoi.priKey())
		tweet_text = stuff[0]
		user = stuff[1]
		movie = stuff[2]
		favorites = stuff[3]
		retweets = stuff[4]
		element_list.append((tweet_text, tweet_id, user, movie, favorites, retweets))

statement = 'INSERT INTO Tweets VALUES (?, ?, ?, ?, ?, ?)'    
for element in element_list:
	try:
		cur.execute(statement, element)
	except:
		pass

# Add data to Movies table:
element_list = []
for maBoi in threeMovies:
		stuff = maBoi.infoList()

		movie_id = int(stuff[4])
		title = maBoi.__str__()
		director = stuff[0]
		languages = stuff[3]
		rating = stuff[1]
		top_actor = stuff[2][0]
		element_list.append((movie_id, title, director, languages, rating, top_actor))

statement = 'INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)'    
for element in element_list:
	try:
		cur.execute(statement, element)
	except:
		pass

conn.commit()


# Make some data base queries to find out interesting information:

	# Grab all the movies with a rating > 7:
movie_tweets = "SELECT title, rating FROM Movies WHERE rating > 7"
cur.execute(movie_tweets)
goodRatings = cur.fetchall()

	# Which are the tweets have been retweeted more than 100 times?
noticed_tweets = "SELECT Tweets.tweet_text, Tweets.retweets, Movies.title, Movies.director FROM Tweets INNER JOIN Movies ON Tweets.movie=movies.title WHERE retweets > 100"
cur.execute(noticed_tweets)
noticed_tweets = cur.fetchall()

	# Grab all the movies with more than 1 language:
movie_actors = "SELECT title, languages FROM Movies WHERE languages > 1"
cur.execute(movie_actors)
multilingual = cur.fetchall()


#Process the acquired data:

# Process the noticed_tweets:
disp = list(set(noticed_tweets))
	# Use a list comprehension to place data in managable way:
disp = [(tup[2], [tup[1], tup[0], tup[3]]) for tup in disp]
	# Use sort function with keyword to sort movies based on how tweeted about they were:
disp = sorted(disp, key=lambda tup: -tup[1][0])

	# Use regex to find the tweets with the phrase "win":
promotionalTweets = 0
for tweet in  disp:
	temp = re.findall("\s?#?[Ww][Ii][Nn]\s", str(tweet[1][1]))
	promotionalTweets = promotionalTweets + len(temp)


	# Define a generator to rate the movies upon output to file:
def outputGen(movieInputs):
	i = 1
	for movie in movieInputs:
		yield str(i) + ". " + movie[0] + " - " + str(movie[1][0]) + " retweets\n" + "		" + str(movie[1][1]) + "\n\n"
		i = i + 1


# Create an output:
output_filename = "206_final_project_output.txt"
f = open(output_filename,'w')

f.write("The following movies were searched for: \n")
for movie in threeMoviez:
	f.write(movie + "\n")

f.write("\nOf those movies, the following were rated above 7 by imdb:\n")
for movie in goodRatings:
	f.write(movie[0] + " - " + movie[1] + "\n")

f.write("\nOf those movies, the following were in more than 1 language:\n")
for movie in multilingual:
	f.write(movie[0] + " - " + str(movie[1]) + " languages\n")

f.write("\n" + disp[0][1][2] + " directed the most tweeted about movie, " + disp[0][0] + "\n")

f.write("\nThese are the tweets about these movies which have been retweeted atleast 100 times, in order:\n")
for guy in outputGen(disp):
	f.write(guy)

f.write("Of these tweets, " + str(promotionalTweets) + " were chances to win free tickets or merch")
f.close()

conn.close()
# Put your tests here, with any edits you now need from when you turned them in with your project plan.

# Test cache loading: 
get_twitter_user("TheRock")
get_twitter_user("Beyonce")
get_twitter_user("HJBenjamin")
get_twitter_user("POTUS")
get_twitter_term("dogville")
get_twitter_term("argo")
get_OMDB_info("Argo")
get_OMDB_info("The Notebook")
get_OMDB_info("night at the museum")
get_OMDB_info("waterworld")

class DataAccessTests(unittest.TestCase):

	def test_twitter_term_len(self):
		self.assertEqual(len(MovieTweets[0][1]), 30)

	def test_twitter_term_caching(self):
		self.assertTrue("Power Rangers_tweets" in cache_dictionary)

	def test_twitter_user_caching(self):
		self.assertTrue("TheRock_user" in cache_dictionary)

	def test_twitter_user_2(self):
		self.assertTrue(get_twitter_user("TheRock")["screen_name"], "TheRock")

	def test_OMDB_info(self):
		self.assertTrue("Hidden Figures" in cache_dictionary)

	def test_get_OMDB_info_success(self):
		self.assertEqual(get_OMDB_info("waterworld")["Director"], "Kevin Reynolds")

class TwitterUsersTests(unittest.TestCase):

	def test_twitterusers_constructor_1(self):
		TwUser = twitterUsers(get_twitter_user("TheRock"))
		self.assertEqual(TwUser.screen_name, "TheRock")

	def test_twitterusers_constructor_2(self):
		TwUser = twitterUsers(get_twitter_user("HJBenjamin"))
		self.assertEqual(TwUser.user_id, 312860399)

	def test_twitterusers_str_1(self):
		TwUser = twitterUsers(get_twitter_user("HJBenjamin"))
		self.assertEqual(type(TwUser.__str__()), type(6))

	def test_twitterusers_str_2(self):
		TwUser = twitterUsers(get_twitter_user("POTUS"))
		self.assertEqual(type(TwUser.__str__()), type(24))

	def test_twitterusers_infoList_1(self):
		TwUser = twitterUsers(get_twitter_user("POTUS"))
		self.assertEqual(TwUser.screen_name, "POTUS")

	def test_twitterusers_infoList_2(self):
		TwUser = twitterUsers(get_twitter_user("Beyonce"))
		self.assertEqual(len(TwUser.infoList()), 3)


class MovieTests(unittest.TestCase):

	def test_movie_constructor_1(self):
		M = Movie(get_OMDB_info("Argo"))
		self.assertEqual(M.director, "Ben Affleck")

	def test__movie_constructor_2(self):
		M = Movie(get_OMDB_info("The Notebook"))
		self.assertEqual(M.IMDB, "7.9")

	def test_movie_str_1(self):
		M = Movie(get_OMDB_info("waterworld"))
		self.assertEqual(M.__str__(), "Waterworld")

	def test_movie_str_2(self):
		M = Movie(get_OMDB_info("night at the museum"))
		self.assertEqual(M.__str__(), "Night at the Museum")

	def test_movie_infoList_1(self):
		M = Movie(get_OMDB_info("waterworld"))
		self.assertEqual(M.infoList(), ["Kevin Reynolds", "6.1", ["Kevin Costner", "Chaim Jeraffi", "Rick Aviles", "R.D. Call"], 1, 114898 ])

	def test_movie_infoList_2(self):
		M = Movie(get_OMDB_info("hidden figures"))
		self.assertEqual(M.infoList(), ["Theodore Melfi", "7.9", ["Taraji P. Henson", "Octavia Spencer", "Janelle Monáe", "Kevin Costner"], 1, 4846340])

class TweetTests(unittest.TestCase):

	def test_tweet_constructor_1(self):
		T = Tweet(get_twitter_term("argo")[0])
		self.assertEqual(type(T.movie), type("Catto"))

	def test_tweet_constructor_2(self):
		T = Tweet(get_twitter_term("night at the museum")[0])
		self.assertEqual(type(T.tweet_id), type(314))

	def test_tweet_str_1(self):
		T = Tweet(get_twitter_term("hidden figures")[0])
		self.assertEqual(type(T.__str__()), type("brouhaha".encode('utf-8')))

	def test_prikey_1(self):
		T = Tweet(get_twitter_term("dogville")[0])
		self.assertEqual(type(T.priKey()),type(6))

	def test_prikey_2(self):
		T = Tweet(get_twitter_term("the boss baby")[0])
		self.assertTrue(T.priKey() > 1)

	def test_tweet_infolist_1(self):
		T = Tweet(get_twitter_term("phoenix forgotten")[0])
		self.assertEqual(len(T.infoList()), 5)

	def test_tweet_infolist_2(self):
		T = Tweet(get_twitter_term("power rangers")[0], "Power Rangers")
		self.assertEqual(T.infoList()[2], "Power Rangers")


class DatabaseTests(unittest.TestCase):

	def test_db_tweets(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		dis = cur.fetchall()
		conn.close()
		self.assertTrue(len(dis)>=3)

	def test_db_movies(self):
		conn = sqlite3.connect('finalproject.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		dat = cur.fetchall()
		conn.close()
		self.assertTrue(len(dat)>=3)


# Remember to invoke your tests so they will run! (Recommend using the verbosity=2 argument.)
if __name__ == "__main__":
	unittest.main(verbosity=2)