#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re
import collections

import numpy as np

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer
from CreateModel import CreateModel
import collections

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'Leroy'
      self.is_turbo = is_turbo
      self.stemmer = PorterStemmer()
      self.read_data()
      self.parsed_sentiment = dict()
      self.model = CreateModel()
      self.negationWords = ["didn't","not","no","don't"]
      self.punctuation = {"but",",",".","!",":",";"}
      self.userMovies = collections.defaultdict()
      self.movieDict = collections.defaultdict(lambda:0)
      self.movie_name_to_id()

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      # TODO: Write a short greeting message                                      #

      greeting_message = "Hi I'm Leroy! I'm your movie best friend. Tell me some moviees you like or hate and I'll share some new ones you might like."

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'Have a nice day!'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        #regex and sentiment analysis
        # hate = negative_word
        #capture all words before movie, "_movie_", everything after
        #look through captured 
        2) transform the information into a response to the user
        # you _negaitve word_ movie
        #let me hear another one
      """

      regex_main = "([\w\s,']*)\"([\w\s(),\:\-\"\'\<\>\?\!\&]*)\"([\w\s,']*)" #three capture groups

      movie_match = ""
      parsed_input = "" 
      response_sentiment = "" #word to describe movie sentiment by bot
      currMovieId = 0

      match = re.findall(regex_main, input)
      print "match: {}".format(match)
      if match == []:
        if len(self.userMovies) == 0:
          response = "Please type a valid response. Movies should be in 'quotations'" #first time user doesn't know how to input text
          return response
        else:
          response = "I want to hear about more movies!"    # edge case when user gets bored
          return response
      else:
        movie_match = match[0][1]
        if movie_match == "":
          response = "Please type a movie within quotation marks"
          return response
        parsed_input = match[0][0] + match[0][2]

        # Check if movie exists!
        if movie_match in self.movieDict:
          currMovieId = self.movieDict[movie_match]
        else:
          response = "Sorry, but that movie is too hip for me! Can you tell me about another?"
          return response

        # FIND PUNCTUATION AND MAKE OWN WORD (ADD SPACE)
        for index,char in enumerate(parsed_input):
          if char in self.punctuation:
            parsed_input = parsed_input[:index] + " " + parsed_input[index:]
        parsed_input = parsed_input.split(" ")
        filter(None, parsed_input)
        print parsed_input

        # EXTRACT SENTIMENT
        pos_words = []
        neg_words = []

        negationTrigger = False   # triggers at neg words
        for word in parsed_input:
          word = self.stemmer.stem(word)
          print word
          if word in self.sentiment:
            sentiment = self.sentiment[word]

            if negationTrigger == True:
              negWord = "pos"
              posWord = "neg"
            else:
              negWord = "neg"
              posWord = "pos"
            if sentiment == negWord:
              neg_words.append(word)
            elif sentiment == posWord:
              pos_words.append(word)

          if word in self.negationWords:
            negationTrigger = True
          if word in self.punctuation:
            negationTrigger = False

        # DETERMINE COUNTS FOR NEG AND POS WORDS
        if len(pos_words) > len(neg_words):
          response_sentiment = "liked"
          self.userMovies[currMovieId] = 1
        elif len(neg_words) > len(pos_words):
          response_sentiment = "disliked"
          self.userMovies[currMovieId] = -1
        elif len(neg_words) == 0 and len(pos_words) == 0:
          print("neutral/no sentiment")
          response = "So how do you feel about %s." %movie_match
          return response
        else:
          print("confused sentiment")
          response = "Sorry, I couldn't quite tell how you feel about %s. Can you tell me more about it?" %movie_match
          return response

        if self.is_turbo == True:
          response = 'processed %s in creative mode!!' % input
        # elif len(self.userMovies) >= 5:
        elif len(self.userMovies) >= 1:
          recommendations = self.recommend(self.userMovies)
          # adding recommendations to response:
          # TODO: Would you like to hear another recommendation? (Or enter :quit if you're done.)
          response = "You %s \"%s\". Thank you! \n That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (response_sentiment, movie_match, recommendations[0])
        else:
          response = "So, you %s \"%s\". How about another movie?" % (response_sentiment, movie_match)


      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def movie_name_to_id(self):
      reader = csv.reader(file('data/movies.txt'), delimiter='%', quoting=csv.QUOTE_MINIMAL)
      for line in reader:
        # not necessary since we want to build movieList
        # if len(userRatings) == len(u):
        #   break
        movieID, title, genres = int(line[0]), line[1], line[2]
        if title[0] == '"' and title[-1] == '"':
          title = title[1:-1]

        self.movieDict[title] = movieID

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings() #TODO: do we need to add this to init()?
      
      # TODO: TEST stem these sentiments
      self.sentiment = collections.defaultdict(lambda:0)
      reader = csv.reader(file('data/sentiment.txt'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
      for line in reader:
        word, posNeg = line[0], line[1]
        word = self.stemmer.stem(word)
        self.sentiment[word] = posNeg
      
      # reader = csv.reader(open('data/sentiment.txt', 'rb'))
      # self.sentiment = dict(reader) #Original: not stemmed
      self.binarize()


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""

      numRows = len(self.ratings)
      numCols = 0
      if numRows > 0:
        numCols = len(self.ratings[0])
      
      for row in range(numRows):
        for col in range(numCols):
          rating = self.ratings[row][col]
          if rating >= 3:
            self.ratings[row][col] = 1
          elif rating != 0:
            self.ratings[row][col] = -1


    # TODO - REMOVE, NO NEED TO HAVE THIS BECUASE SIMILARITY IS NP.DOT()
    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # Implement the distance function between vectors u and v
      # Note: you can also think of this as computing a similarity measure
      # Method: cosine similarity

      # cosineSimilarity = 0.0
      # uNorm = 0.0
      # vNorm = 0.0
      # for i in range(len(u)):
      #     cosineSimilarity += u[i] * v[i]
          # uNorm += u[i] * u[i]
          # vNorm += v[i] * v[i]
      
      # Normalize - NO NEED TO NORMALIZE
      # uNorm = math.sqrt(uNorm)
      # vNorm = math.sqrt(vNorm)
      # cosineSimilarity = cosineSimilarity / (uNorm * vNorm)

      # TODO: check warning
      #     /Users/kevinliao/Documents/CS124/Assignment6/cs124-chatbot/chatbot.py:254: RuntimeWarning: invalid value encountered in double_scalars
      # cosineSimilarity = cosineSimilarity / (uNorm * vNorm)

      # return cosineSimilarity


    def recommend(self, userRatings):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # Implemented a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      # Notes: input 'u' is self.userMovies (movieID, rating)

      estRatings = collections.defaultdict(lambda:0)

      print "Starting For Loop"

      for movieA in range(len(self.titles)):
        rating = 0.0

        #if movieA is in any movieB, don't recommend
        if movieA in userRatings:
          continue

        for movieB in userRatings:
          similarity = np.dot(self.ratings[movieA],self.ratings[movieB])
          userRating = userRatings[movieB]
          rating += similarity * userRating

        estRatings[movieA] = rating
      print "Ending For Loop"

      #TODO: make sure recommendations is length of 3
      max_value = max(estRatings.values())
      max_keys = [k for k, v in estRatings.items() if v == max_value] # getting all keys containing the `maximum`
      recommendations = []
      for keys in max_keys:
        movieName = [k for k, v in self.movieDict.items() if v == keys]
        recommendations.append(movieName[0])

      return recommendations



    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """
    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
