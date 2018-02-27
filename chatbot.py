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
      self.strongPosVerbs = {"love","loved","adored","adore","enjoy","enjoyed"}
      self.strongPosAdjectives = {"amazing","cool","awesome","favorite"}
      self.strongNegVerbs = {"hate","hated","abhored","abhor","loathed","loathe","dispised","dispise"}
      self.strongNegAdjectives = {"apalling"}
      self.intensifiersSubject = {"really","reeally","extremely","absolutely"}
      self.intensifiersObject = {"really","reeally","very","extremely","remarkably","unusually","utterly","absolutely","exceptionally"}

      self.userMovies = collections.defaultdict()
      self.movieDict = collections.defaultdict(lambda:0)
      self.movie_name_to_id()
      self.movie_history = []

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

      # if self.turbo == True:
      #   regex_multiple_movies = "([\w\s,']*)\"([\w\s(),\:\-\"\'\<\>\?\!\&]*)\"([\w\s,']*)(?:\"([\w\s(),\:\-\"\'\<\>\?\!\&]*)\"([\w\s,']*))*"
      #   movie_matches = []
      #   parsed_input = ""
      #   response_sentiment = ""
      #   match = re.findall(regex_main, input)

      # if match == []:
      #   if len(self.userMovies) == 0:
      #     response = "Please type a valid response. Movies should be in 'quotations'" #first time user doesn't know how to input text
      #     return response
      #   else:
      #     response = "I want to hear about more movies!"    # edge case when user gets bored
      #     return response
      # else:
      #   for i, movie in enumerate(match):
      #     movie_match.append(match[0][i*2 + 1])
      #   for movie in movie_match:

      #     #movie_match = match[0][1]
      #     if movie == "":
      #       response = "Please type a movie within quotation marks"
      #       return response
      #     parsed_input = match[0][0] + match[0][2]

      #   # Check if movie exists!
      #     if movie_match in self.movieDict:
      #       currMovieId = self.movieDict[movie_match]
      #     else:
      #       response = "I could not find one of those movies"
      #       return response

      #   # FIND PUNCTUATION AND MAKE OWN WORD (ADD SPACE)
      #     for index,char in enumerate(parsed_input):
      #       if char in self.punctuation:
      #         parsed_input = parsed_input[:index] + " " + parsed_input[index:]
      #     parsed_input = parsed_input.split(" ")
      #     filter(None, parsed_input)
      #   else:

      #save movie and sentiment
      #it, that, 
      #"any word" or it and that

      #if self.turbo == True:
      regex_main = "([\w\s,']*)(it|that|\"[()-.\w\s]*\")([\w\s,']*)"
       

      #regex_main = "([\w\s,']*)\"([\w\s(),\:\-\"\'\<\>\?\!\&]*)\"([\w\s,']*)" #three capture groups

      movie_match = ""
      parsed_input = "" 
      currMovieId = 0

      match = re.findall(regex_main, input)
      # print "match: {}".format(match)
      if match == []:
        if len(self.userMovies) == 0:
          return "Please type a valid response. Movies should be in 'quotations'" #first time user doesn't know how to input text
        else:
          return "I want to hear about more movies!"    # edge case when user gets bored
      else:
        movie_match = match[0][1].replace('"', "")
        if movie_match == "":
          return "Please type a movie within quotation marks"
        parsed_input = match[0][0] + match[0][2]

        #CODE FOR REMEMBERING MOVIE INPUTS

        if movie_match == "it" or movie_match == "that":
          if len(self.movie_history) > 0:
            movie_match = self.movie_history[len(self.movie_history) - 1]
          else:
            response = "I'm sorry, I don't know what \"%s\" is. Please input a movie!" %movie_match
            return response

        self.movie_history.append(movie_match)
        #END CODE FOR REMEMBERING MOVIE INPUTS!



        # Check if movie exists!
        if movie_match in self.movieDict:
          currMovieId = self.movieDict[movie_match]
        else:
          return "Sorry, but that movie is too hip for me! Can you tell me about another?"

        

        # FIND PUNCTUATION AND MAKE OWN WORD (ADD SPACE)
        for index,char in enumerate(parsed_input):
          if char in self.punctuation:
            parsed_input = parsed_input[:index] + " " + parsed_input[index:]
        parsed_input = parsed_input.split(" ")
        filter(None, parsed_input)

        # EXTRACT SENTIMENT
        pos_words = []
        neg_words = []

        #INITIALIZE RESPONSE VARIABLES
        negationTrigger = False   # triggers at neg words
        objectTrigger = False     # triggers based on sentence strucutre (I really like star wars versus, star wars was really bad)
        response_intensifier = ""
        response_verb = ""
        response_adjective = ""

        for word in parsed_input:

          # INTENSIFIERS
          if word in self.intensifiersSubject:
            response_intensifier = word
          if word in self. intensifiersObject:
            response_intensifier  = word
            objectTrigger = True

          if word in self.strongPosAdjectives or word in self.strongNegAdjectives:
            objectTrigger = True
            response_adjective = word
          if word in self.strongPosVerbs or word in self.strongNegVerbs:
            response_verb = word

          word = self.stemmer.stem(word)

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

        if len(neg_words) == len(pos_words) and response_adjective == "" and response_verb == "": # IF NO POS AND NEG (INCLUDING STRONG ONES WE HARD CODE)
          return "So how do you really feel about %s." %movie_match
        elif len(pos_words) > len(neg_words):
          if response_adjective == "": 
            response_adjective = "good"
          if response_verb == "": 
            response_verb = "liked"
          self.userMovies[currMovieId] = 1
        elif len(neg_words) > len(pos_words) and not objectTrigger:
          if response_adjective == "": 
            response_adjective = "bad"
          if response_verb == "": 
            response_verb = "disliked"
          self.userMovies[currMovieId] = -1

        # APPEND INTENSIFIER IN RESPONSE
        if response_intensifier != "":
          if objectTrigger:
            response_adjective = response_intensifier + " " + response_adjective
          else:
            response_verb = response_intensifier + " " + response_verb


        ############# RESPONSES #################
        if self.is_turbo == True:
          response = 'processed %s in creative mode!!' % input
        elif len(self.userMovies) >= 4:
          recommendations = self.recommend(self.userMovies)

          # TODO: Would you like to hear another recommendation? (Or enter :quit if you're done.)
          if objectTrigger:
            response = "You thought \"%s\" was %s. Thank you! \n That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (movie_match, response_adjective, recommendations[0])
          else:
            response = "You %s \"%s\". Thank you! \n That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (response_verb, movie_match, recommendations[0])
        else:
          if objectTrigger:
            response = "So, you thought \"%s\" was %s. How about another movie?" % (movie_match, response_adjective)
          else:
            response = "So, you %s \"%s\". How about another movie?" % (response_verb, movie_match)

      return response


    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def movie_name_to_id(self):
      reader = csv.reader(file('data/movies.txt'), delimiter='%', quoting=csv.QUOTE_MINIMAL)
      for line in reader:
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


    def recommend(self, userRatings):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # Implemented a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      # Notes: input 'u' is self.userMovies (movieID, rating)

      estRatings = collections.defaultdict(lambda:0)

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
      CREATIVE EXTENSIONS
      1) Fine-Tune Sentiment - bot responds to certain strong words and intensifiers 
      TODO: make this impact sentiment analysis? - non-binarize?
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
