#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re

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
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.read_data()
      self.parsed_sentiment = dict()
      self.model = CreateModel()
      self.negationWords = ["didn't","not","no"]
      self.punctuation = {"but",",",".","!",":",";"}
      self.stemmer = PorterStemmer()
      self.userMovies = collections.defaultdict()
      self.sentiment = collections.defaultdict()

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      # TODO: Write a short greeting message                                      #

      greeting_message = 'How can I help you?'

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
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      print self.userMovies

      if len(self.userMovies) < 5:
        return self.getMoreMovies(input)
      else:
        self.reccomend()

    def getMoreMovies(self,input):
      regexes = []
      regex_main = "([\w\s,]*)\"([\w\s]*)\"([\w\s,]*)" #three capture groups

      match = []
      movie_match = ""
      words_to_sentiment = ""
      response_sentiment = ""


      match = re.findall(regex_main, input)
      # print match
      if match == []:
        if len(self.userMovies) == 0:
          response = "Please type a valid response. Movies should be in 'quotations'"
          return response
        else:
          response = "Wait, this is interesting! Tell me about more movies"
      else:
        movie_match = match[0][1]
        if movie_match == "":
          response = "please type a movie within quotation marks"
        words_to_sentiment = match[0][0] + match[0][2]

        #found_sentiment_words = []
        #print (self.sentiment)
        for index,char in enumerate(words_to_sentiment):
          if char in self.punctuation:
            words_to_sentiment = words_to_sentiment[:index] + " " + words_to_sentiment[index:]

        words_to_sentiment = words_to_sentiment.split(" ")
        filter(None, words_to_sentiment)
        # self.model.classifyTest(words_to_sentiment)

        # attempted sentiment analysis
        pos_words = []
        neg_words = []

        negationTrigger = False
        for word in words_to_sentiment:
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

        if len(pos_words) > len(neg_words):
          response_sentiment = "liked"
          self.userMovies[movie_match] = "1"
        elif len(neg_words) > len(pos_words):
          response_sentiment = "disliked"
          self.userMovies[movie_match] = "-1"
        else:
          print("neutral/no sentiment")
          response = "Sorry, I couldn't quite tell how you feel about %s. Can you tell me more about it?" %movie_match
          return response

        if self.is_turbo == True:
          response = 'processed %s in creative mode!!' % input
        else:
          # response = 'processed %s in starter mode' % input
          response = "So, you %s %s" % (response_sentiment, movie_match)

      if len(self.userMovies) >= 5:
        self.recommend()
      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      # for sentiment in reader:
      #   self.sentiment[sentiment] = self.stemmer.stem(sentiment)
      self.sentiment = dict(reader)


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""

      pass


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      pass


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      pass


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
