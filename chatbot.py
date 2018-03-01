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
      self.negationWords = ["didn't","not","no","don't"]
      self.punctuation = {"but",",",".","!",":",";"}
      self.strongPosVerbs = {"love","loved","adored","adore","enjoy","enjoyed"}
      self.strongPosAdjectives = {"amazing","cool","awesome","favorite"}
      self.strongNegVerbs = {"hate","hated","abhored","abhor","loathed","loathe","dispised","dispise"}
      self.strongNegAdjectives = {"apalling"}
      self.intensifiersSubject = {"really","reeally","extremely","absolutely"}
      self.intensifiersObject = {"really","reeally","very","extremely","remarkably","unusually","utterly","absolutely","exceptionally"}
      self.corrected_movie_trigger = False

      #For Two movie input

      self.similarity_words = {"either", "neither", "both", "and"}
      self.disimilarity_words = {"but"} #TODO: any more?

      #End Two Movie Input

      self.userMovies = collections.defaultdict()
      self.movieDict = collections.defaultdict(lambda:0)
      self.genreDict = collections.defaultdict(lambda:0)
      self.movieNameList = []
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

    def LD(self, s, t, costs=(1, 1, 1)):
      """ 
          iterative_levenshtein(s, t) -> ldist
          ldist is the Levenshtein distance between the strings 
          s and t.
          For all i and j, dist[i,j] will contain the Levenshtein 
          distance between the first i characters of s and the 
          first j characters of t
          
          costs: a tuple or a list with three integers (d, i, s)
                 where d defines the costs for a deletion
                       i defines the costs for an insertion and
                       s defines the costs for a substitution
      """
      rows = len(s)+1
      cols = len(t)+1
      deletes, inserts, substitutes = costs
      
      dist = [[0 for x in range(cols)] for x in range(rows)]
      # source prefixes can be transformed into empty strings 
      # by deletions:
      for row in range(1, rows):
          dist[row][0] = row * deletes
      # target prefixes can be created from an empty source string
      # by inserting the characters
      for col in range(1, cols):
          dist[0][col] = col * inserts
          
      for col in range(1, cols):
          for row in range(1, rows):
              if s[row-1] == t[col-1]:
                  cost = 0
              else:
                  cost = substitutes
              dist[row][col] = min(dist[row-1][col] + deletes,
                                   dist[row][col-1] + inserts,
                                   dist[row-1][col-1] + cost) # substitution
      #for r in range(rows):
          #print(dist[r])
      
   
      return dist[row][col]
  # default:
  #print(iterative_levenshtein("abc", "xyz"))
  # the costs for substitions are twice as high as inserts and delets:
  #print(iterative_levenshtein("abc", "xyz", costs=(1, 1, 2)))
  # inserts and deletes are twice as high as substitutes
  #print(iterative_levenshtein("abc", "xyz", costs=(2, 2, 1)))
  #print(iterative_levenshtein("flaw", "lawn"))

    # def LD(self, s, t):
    #   if s == "":
    #     return len(t)
    #   if t == "":
    #     return len(s)
    #   if s[-1] == t[-1]:
    #     cost = 0
    #   else:
    #     cost = 1
       
    #   res = min([self.LD(s[:-1], t)+1,
    #            self.LD(s, t[:-1])+1, 
    #            self.LD(s[:-1], t[:-1]) + cost])
    #   return res
#print(LD("Python", "Peithen"))

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


      #regex_main = "([\w\s,']*)(it|that|\"[()-.\w\s]*\")([\w\s,']*)" #For doing history/remembering
      if self.corrected_movie_trigger == False:
        regex_main = "([\w\s,']*)(it|that|It|That|\"[()-.\w\s]*\")([\w\s,']*)(?:\"([\w\s(),]*)\"([\w\s,']*))*" # includes BOTH two-movie feature AND remembering-history feature
      else:
        regex_main = "(no|No|yes|Yes)()()()" #FOR REPONSE TO MOVIE CORRECTION FEATURE, ONLY WNAT YES OR NO

      #history doesn't really work for TWO movies, it only remembers first movie in the two
      #regex_main = "([\w\s,']*)\"([\w\s(),\:\-\"\'\<\>\?\!\&]*)\"([\w\s,']*)" #three capture groups

      movie_match = ""
      movie_match_2 = "" #second movie
      two_movie_matches = []
      parsed_input = "" 
      currMovieId = -1
      currMovieId2 = -1 #same method for dealing with a second movie


      match = re.findall(regex_main, input)
      # print "match: {}".format(match) # DEBUGGING info
      if match == []:
        if len(self.userMovies) == 0:
          return "Please type a valid response. Movies should be in 'quotations'" #first time user doesn't know how to input text
        else:
          return "I want to hear about more movies!"    # edge case when user gets bored
      else:
        movie_match = match[0][1].replace('"', "")
        movie_match_2 = match[0][3].replace('"', "") # adds second movie, might be NULL string if single movie
        parsed_input = match[0][0] + match[0][2]

         # FIND PUNCTUATION AND MAKE OWN WORD (ADD SPACE)
        for index,char in enumerate(parsed_input):
          if char in self.punctuation:
            parsed_input = parsed_input[:index] + " " + parsed_input[index:]
        parsed_input = parsed_input.split(" ")
        filter(None, parsed_input)

        if parsed_input[0] == "No" or parsed_input[0] == "no": #IF USER INPUTS NO FOR CONFIRMING MOVIE
          if self.corrected_movie_trigger == True:
            self.corrected_movie_trigger = False
            return "Hmmm... okay then. Can you retype the movie or talk about another one?"
        elif parsed_input[0] == "Yes" or parsed_input[0] == "yes": #IF USER INPUTS YES FOR CONFIRMING MOVIE
          if self.corrected_movie_trigger == True:
            self.corrected_movie_trigger = False
            movie_match = self.movie_history[len(self.movie_history) - 1]
        if movie_match == "" and self.corrected_movie_trigger == False:
          return "Please type a movie within quotation marks"
        

        #CODE FOR REMEMBERING MOVIE INPUTS
        if movie_match == "it" or movie_match == "that" or movie_match == "It" or movie_match == "That": #if someone references it or that without a movie
          if len(self.movie_history) > 0:
            movie_match = self.movie_history[len(self.movie_history) - 1]
          else:
            response = "I'm sorry, I don't know what \"%s\" is. Please input a movie!" %movie_match
            return response

        

        #END CODE FOR REMEMBERING MOVIE INPUTS!


        #CHECK IF MOVIES EXISTS 
        min_distance = 1000
        corrected_movie = ""


        if movie_match in self.movieDict:
          currMovieId = self.movieDict[movie_match]
          self.movie_history.append(movie_match)
        else:
          for movie in self.movieDict:
            edit_distance = self.LD(movie, movie_match) # check for smallest edit distance
            if edit_distance < min_distance:
              corrected_movie = movie
              min_distance = edit_distance
          self.corrected_movie_trigger = True
          self.movie_history.append(corrected_movie)
          return "Sorry, did you mean \"%s\"?" %corrected_movie #ask for "best" movie
          #return "Sorry, but that movie is too hip for me, or it might not exist! Can you tell me about another movie?"
        if movie_match_2 in self.movieDict: #checks if second movie exists
          currMovieId2 = self.movieDict[movie_match_2]


       

        # EXTRACT SENTIMENT
        pos_words = []
        neg_words = []

        #INITIALIZE RESPONSE VARIABLES

        opposite_sentiment_trigger = False # User has different feelings about two movies
        same_sentiment_trigger = False #User has same feelings about two movies

        negationTrigger = False   # triggers at neg words
        objectTrigger = False     # triggers based on sentence strucutre (I really like star wars versus, star wars was really bad)
        response_intensifier = ""
        response_verb = ""
        response_verb_2 = "" #for second movie
        response_adjective = ""
        response_adjective_2 = "" # for second movie

        for word in parsed_input:

          # CHECKING FOR SIMILARITY WORDS WHEN TWO MOVIES EXIST

          if word in self.disimilarity_words:
            opposite_sentiment_trigger = True #if found words like "but"
          if word in self.similarity_words:
            same_sentiment_trigger = True #if found words like "both"


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
          print self.userMovies[currMovieId]

          #PART OF MULTIPLE MOVIE CODE
          if currMovieId2 != -1: #if there is a second movie
            if same_sentiment_trigger == True and opposite_sentiment_trigger == False: #if sentiment for two movies is same
              self.userMovies[currMovieId2] = 1
              response_verb_2 = response_verb
              response_adjective_2 = response_adjective
            elif same_sentiment_trigger == False and opposite_sentiment_trigger == True:
              self.userMovies[currMovieId2] = -1
              response_verb_2 = "disliked"
              response_adjective_2 = "bad"
            else:
              response = "I don't know how you felt about those two movies, could you clarify for me?"
              return response

          #END PART OF MULTIPLE MOVIE CODE

        elif len(neg_words) > len(pos_words) and not objectTrigger:
          if response_adjective == "": 
            response_adjective = "bad"
          if response_verb == "": 
            response_verb = "disliked"
          self.userMovies[currMovieId] = -1
          print self.userMovies[currMovieId]


          #PART OF MULTIPLE MOVIE CODE
          if currMovieId2 != -1: # if there is a second movie
            if same_sentiment_trigger == True and opposite_sentiment_trigger == False: 
              self.userMovies[currMovieId2] = -1
              response_verb_2 = response_verb
              response_adjective_2 = response_adjective
            elif same_sentiment_trigger == False and opposite_sentiment_trigger == True:
              self.userMovies[currMovieId2] = 1
              response_verb_2 = "liked"
              response_adjective = "good"
            else:
              response = "I don't know how you felt about those two movies, could you clarify for me?"
              return response

        # APPEND INTENSIFIER IN RESPONSE
        if response_intensifier != "":
          if objectTrigger:
            response_adjective = response_intensifier + " " + response_adjective
          else:
            response_verb = response_intensifier + " " + response_verb


        ############# RESPONSES #################
        if self.is_turbo == True:
          response = 'processed %s in creative mode!!' % input
        else:
          if objectTrigger:
            response = "So, you thought \"%s\" was %s " % (movie_match, response_adjective)
            if currMovieId2 != -1:
              response += "and  %s was \"%s\" " %(movie_match_2, response_adjective_2) #append if second movie exists
          else:
            response = "So, you %s \"%s\" " % (response_verb, movie_match)
            if currMovieId2 != -1:
              response += "and you %s \"%s\" " %(response_verb_2, movie_match_2) #append if second movie exists


          # CHECK FOR MORE MOVEIS NEEDED OR RECOMMENDATION MADE
          if len(self.userMovies) >= 4:
            recommendations = self.recommend(self.userMovies)

            # TODO: Would you like to hear another recommendation? (Or enter :quit if you're done.)
            if objectTrigger:
              response += "Thank you! \n That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (recommendations[0])
            else:
              response += "Thank you! \n That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (recommendations[0])
          else:
            response += "How about another movie?"

          #START INQUIRING ABOUT THEIR MOVIE PREFERENCE GENRES
          # if len(self.userMovies) >= 2:
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
        genres = genres.split("|")
        self.movieDict[title] = movieID
        self.genreDict[title] = genres
        self.movieNameList.append(title)

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
      
      # Original: not stemmed
      # reader = csv.reader(open('data/sentiment.txt', 'rb'))
      # self.sentiment = dict(reader) 
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
        if movieA in userRatings: # if movieA is in any movieB, don't recommend
          continue
        for movieB in userRatings:
          similarity = np.dot(self.ratings[movieA],self.ratings[movieB])
          userRating = userRatings[movieB]
          rating += similarity * userRating
        estRatings[movieA] = rating

      recommendations = []
      recommendationCounter = collections.Counter(estRatings)
      for movieID, rating in recommendationCounter.most_common(3):
        recommendations.append(self.movieNameList[movieID]) # Note: movieID happens to be same as index of movie in list
      # print 'recommendation list: {}'.format(recommendations) #DEBUGGING INFO
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
      # TODO: update this when you are working on new creative extentions!!!
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
