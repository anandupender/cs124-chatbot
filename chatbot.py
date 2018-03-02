#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Modified by Anand Upender, Chase Lortie, Kevin Liao
######################################################################
import csv
import math
import re
import collections
import numpy as np

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'Leroy'
      self.userName = ''
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
      self.userEmotions = [0,0,0,0,0] # anger, disgust, fear, joy, sadness
      self.movieDict = collections.defaultdict(lambda:0)
      self.genreDict = collections.defaultdict(lambda:0)
      self.movieIDToName = collections.defaultdict(lambda:0)
      self.movie_name_to_id()
      self.movie_history = []
      self.movie_recommendations = []

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      # A short greeting message                                      #
      greeting_message = "Hi I'm Leroy! I'm your movie best friend. Tell me some movies you like or hate and I'll share some new ones you might like. \n What is your name?"
      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # A short farewell message                                      #
      #############################################################################
      goodbye_message = 'Aww... I hope to see you again soon '
      if self.userName == '':
        goodbye_message += 'my friend!'
      else:
        goodbye_message += self.userName + '!'
      goodbye_message += ' Have a nice day!'

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

      if self.corrected_movie_trigger == False and len(self.movie_recommendations) == 0:
        regex_main = "([\w\s,']*)(\b(?:it|that|It|That)\b|\"[()-.,':\w\s]*\")([\w\s,']*)(?:\"([\w\s(),]*)\"([\w\s,']*))*" # includes BOTH two-movie feature AND remembering-history feature
      else:
        regex_main = "(no|No|yes|Yes)()()()" #FOR REPONSE TO MOVIE CORRECTION FEATURE, ONLY WANT YES OR NO

      # PRIVATE INSTANCE VARIABLES 
      movie_match = ""
      movie_match_2 = "" #second movie
      # two_movie_matches = []  #Can remove?
      parsed_input = "" 
      currMovieId = -1
      currMovieId2 = -1 #same method for dealing with a second movie

      match = re.findall(regex_main, input)
      # print "match: {}".format(match) # DEBUGGING info

      if match == []:
        #CODE FOR REMEMBERING MOVIE INPUTS
        referenceWord = ['it','It','that','That']
        parsed_input = self.parseInput(input)
        intersection = list(set(parsed_input) & set(referenceWord))
        if len(intersection) > 0 and len(self.movie_history) > 0: #if someone references it or that without a movie
          movie_match = self.movie_history[len(self.movie_history) - 1]
        else:
          return self.noMatchHelper(input)

      if movie_match == "":
        movie_match = match[0][1].replace('"', "")
        movie_match_2 = match[0][3].replace('"', "") # adds second movie, might be NULL string if single movie
      if parsed_input == "":
        parsed_input = match[0][0] + match[0][2]
        parsed_input = self.parseInput(parsed_input)

      # CONFIRMING SPELL CHECK RECOMMENDATION OR CONTINUED MOVIE RECOMMENDATION
      if parsed_input[0] == "No" or parsed_input[0] == "no": #IF USER INPUTS NO FOR CONFIRMING MOVIE
        if self.corrected_movie_trigger == True:  #SPELL CHECK RECOMMENDATION
          self.corrected_movie_trigger = False
          return "Hmmm... okay then. Can you retype the movie or talk about another one?"
        if len(self.movie_recommendations) != 0:  #CONTINUE MOVIE RECOMMENDATION
          self.movie_recommendations = []
          return " Got it! \n Tell me some more movies you like or hate! \n Or enter \":quit\" if you're done, but I hope you don't want to leave yet."
      elif parsed_input[0] == "Yes" or parsed_input[0] == "yes": #IF USER INPUTS YES FOR CONFIRMING MOVIE
        if self.corrected_movie_trigger == True:  #SPELL CHECK
          self.corrected_movie_trigger = False
          movie_match = self.movie_history[len(self.movie_history) - 1]
        if len(self.movie_recommendations) != 0:  #CONTINUE MOVIE RECOMMENDATION
          recommendation = self.movie_recommendations.pop(0)
          response = " I also suggest you watch \"%s\"" % (recommendation)
          if len(self.movie_recommendations) == 0:
            response += " Those are some quick recommendations! Tell me some more movies you like or hate! \n Or enter \":quit\" if you're done, but I hope you don't want to leave yet."
          else:
            response += " Would you like to hear another recommendation? Please respond with yes or no."
          return response

      # EDGE CASE: WHEN USER ENTERS EMPTY QUOTATIONS
      if movie_match == "":
        return "Please type a movie within quotation marks"

      # CODE FOR REMEMBERING MOVIE INPUTS # TODO(anand): do we still need this? I moved the logic upward
      if movie_match == "it" or movie_match == "that" or movie_match == "It" or movie_match == "That": #if someone references it or that without a movie
        if len(self.movie_history) > 0:
          movie_match = self.movie_history[len(self.movie_history) - 1]
        else:
          response = "I'm sorry, I don't know what \"%s\" is. Please input a movie!" %movie_match
          return response

      # CHECK IF MOVIES EXISTS AND GIVES SUGGESTION 
      min_distance = 1000
      corrected_movie = ""
      if movie_match in self.movieDict:
        for mID in self.userMovies:
          if movie_match == self.movieIDToName[mID]:
            return "Already got that! Please give me another movie!"
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
        return "Sorry, did you mean \"%s\"? Please respond with yes or no." %corrected_movie #ask for "best" movie
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
        # print self.userMovies[currMovieId]

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
        # print self.userMovies[currMovieId]

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
      # CLARIFICATION: already in creative mode
      # if self.is_turbo == True:
      #   response = 'processed %s in creative mode!!' % input
      if objectTrigger:
        response = "So, you thought \"%s\" was %s" % (movie_match, response_adjective)
        if currMovieId2 != -1:
          response += " and  %s was \"%s\"" %(movie_match_2, response_adjective_2) #append if second movie exists
        else:
          response += "."
      else:
        response = "So, you %s \"%s\"" % (response_verb, movie_match)
        if currMovieId2 != -1:
          response += " and you %s \"%s\"" %(response_verb_2, movie_match_2) #append if second movie exists
        else:
          response += "."

      #START INQUIRING ABOUT THEIR MOVIE PREFERENCE GENRES
      response += self.genrePatternHelper()

      # CHECK FOR MORE MOVEIS NEEDED OR RECOMMENDATION MADE
      if len(self.userMovies) < 5:  #TODO: need to check if bot takes at least 5 movies
        response += " How about another movie?"
      else:
        self.movie_recommendations = self.recommend(self.userMovies)
        recommendation = self.movie_recommendations.pop(0)
        if self.userName == "":
          response += " \n Thank you! That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (recommendation)
        else:
          response += " \n Thank you " + self.userName + "! That's enough for me to make a recommendation. \n I suggest you watch \"%s\"" % (recommendation)
        response += " Would you like to hear another recommendation? Please respond with yes or no."


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
        self.movieIDToName[movieID] = title

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      self.sentiment = collections.defaultdict(lambda:0)
      reader = csv.reader(file('deps/sentiment.txt'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
      for line in reader:
        word, posNeg = line[0], line[1]
        word = self.stemmer.stem(word)
        self.sentiment[word] = posNeg

      # CM6 - RESPOND TO EMOTION
      self.emotion = collections.defaultdict(lambda:0)
      emotionReader = csv.reader(file('deps/emotions.txt'), delimiter=',', quoting=csv.QUOTE_MINIMAL)
      for line in emotionReader:
        currEmotion = line[0]
        line = map(int, line[1:])
        self.emotion[currEmotion] = line

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
      for movieID, rating in recommendationCounter.most_common(5):
        recommendations.append(self.movieIDToName[movieID]) # Note: movieID happens to be same as index of movie in list
      # print 'recommendation list: {}'.format(recommendations) #DEBUGGING INFO
      return recommendations

    ####### ADDITIONAL HELPER FUNCTIONS ########
    def parseInput(self, myInput):
       # FIND PUNCTUATION AND MAKE OWN WORD (ADD SPACE)
      parsed_input = []
      for index,char in enumerate(myInput):
        if char in self.punctuation:
          myInput = myInput[:index] + " " + myInput[index:]
      parsed_input = myInput.split(" ")
      filter(None, parsed_input)
      return parsed_input

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

    def noMatchHelper(self, raw_input):
      # (CM6: Emotion detection)
      parsed_input = self.parseInput(raw_input)
      currInputEmotion = [0,0,0,0,0]
      for word in parsed_input:
        if word in self.emotion:
          for index, emotion in enumerate(self.emotion[word]):
            if emotion == 1:      # if this word has this emotion
              self.userEmotions[index] += 1
              currInputEmotion[index] += 1
      
      return self.arbitraryInputHelper(raw_input, currInputEmotion)

    # (CM5 Arbitrary input and CM6 Identifying and responding to emotions)
    def arbitraryInputHelper(self, rawInput, currInputEmotion):
      rawInput = re.sub('[!?]', '', rawInput)
      userInput = rawInput.split(' ')
      userInputLowerCase = rawInput.lower().split(' ')
      rawResponse = self.reverseSubject(userInput)
      # print rawResponse # DEBUGGING

      # (add onto CM1) Easter egg: anything containing Leroy
      if 'leroy' in userInputLowerCase:
        return "That's my name!"
      if userInputLowerCase[0:] == ["what","movies","do","you","like"]:
        return "I like Interstellar a lot. How about movies you like?"

      # Get user name!
      if userInputLowerCase[0:3] == ["my","name","is"]:
        self.userName = ' '.join(userInput[3:])
        return "Hi " + self.userName + "!"
      if userInputLowerCase[0:2] == ["i","am"]:
        self.userName = ' '.join(userInput[2:])
        return "Hi " + self.userName + "!"

      # Utilizes user input
      if userInputLowerCase[0] == "can" and userInputLowerCase[1] == "i": 
        return "I don't know if you can " + ' '.join(rawResponse[2:]) + "."
      elif userInputLowerCase[0] == "can" and userInputLowerCase[1] == "you":
        return "I don't know if I can " + ' '.join(rawResponse[2:])  + "."
      elif userInputLowerCase[0] == "what":
        if userInputLowerCase[1:4] == ["is","my","name"]:
          if self.userName != '':
            return "Your name is " + self.userName + "!"
          else:
            return "I don't know your name yet. What is your name?"
        if "do" not in userInputLowerCase and "does" not in userInputLowerCase:
          return "I don't know what " + ' '.join(rawResponse[2:]) + ' ' + rawResponse[1]  + "."
        else:
          return "Sorry, I don't know."
      elif userInputLowerCase[0] == "who":
        return "Hmm..."
      elif userInputLowerCase[0] == "where":
        return "Maybe in your basement?"
      elif userInputLowerCase[0] == "when":
        return "I don't know when. I'm not your secretary."
      elif userInputLowerCase[0] == "why":
        return "Why... that's a good question."
      elif userInputLowerCase[0] == "how":
        return "I don't know how. But I'd love to hear about some movies you've watched!"
        # return "I don't know how " + ' '.join(rawResponse[2:]) + ' ' + rawResponse[1]

      # anger, disgust, fear, joy, sadness
      random = randint(0, 3)
      angryResponses = ["Don't get upset at me, I'm just the messenger.","I'm sorry, this is a frowny-face-free zone","If I could get mad at you I would.","Don't raise your voice at me!"]
      disgustedResponses = ["Wow don't get that grossed out", "That was uncalled for","Ok...not sure how to react to that.","Wow don't get that grossed out"]
      fearResponses = ["Don't be scared! Everything will be ok.","Well now I'm scared too!","It's just a movie, don't be scared!", "I'm your friend, don't get scared."]
      happyResponses = ["You getting happy makes me happy!","I love your enthusiasm!","Woah there, don't get too excited...","Glad, you're happy...I'm for sure not."]
      sadResponses = ["I am sorry you are sad. Want a tissue?","Build a bridge and get over it.","Know what tears are? Water? Know what computers don't like? You guessed it!","Know what tears are? Water? Know what computers don't like? You guessed it!"]
      defaultResponses = ["Hmm, not sure I get your point.","Wait what, say that again.","Yea...I'm not following.","We're not on the same page right now.","Got it. Why don't we talk about movies some more?"]
      if not all(v == 0 for v in currInputEmotion):  # FOUND EMOTION

        if currInputEmotion[0] == 1:
          return angryResponses[random]
        elif currInputEmotion[1] == 1:
          return disgustedResponses[random]
        elif currInputEmotion[2] == 1:
          return fearResponses[random]
        elif currInputEmotion[3] == 1:
          return happyResponses[random]
        elif currInputEmotion[4] == 1:
          return sadResponses[random]

      else:
        if len(self.userMovies) == 0:
          return defaultResponses[random] + " Please type a movie within quotation marks."
        return defaultResponses[random] #+ " Are you sure we are still talking about movies?"

    def reverseSubject(self, userInput):
      rawResponse = []
      prev = ""
      for idx in range(len(userInput)):
        word = userInput[idx]
        if word == 'i' or word == 'I':
          rawResponse.append('you')
          if prev == 'am':
              rawResponse[idx-1] = 'are'
        elif word == 'me':
          rawResponse.append('you')
        elif word == 'you':
          if idx == len(userInput)-1:
            rawResponse.append('me')
          else:
            rawResponse.append('I')
            if prev == 'are':
              rawResponse[idx-1] = 'am'
        elif word == 'are':
          if prev == 'i' or prev == 'I':
            rawResponse[idx-1] = 'am'
        elif word == 'am':
          if prev == 'you':
            rawResponse[idx-1] = 'are'
        else:
          rawResponse.append(word)
        prev = word
      return rawResponse

    def genrePatternHelper(self):
      userGenresPos = collections.defaultdict(lambda:0)
      userGenresNeg = collections.defaultdict(lambda:0)
      mostPopGenre = ""
      leastPopGenre = ""

      for movie in self.userMovies:
        for genre in self.genreDict[self.movieIDToName[movie]]:
          if self.userMovies[movie] == 1: #they like the movie
            userGenresPos[genre] += 1
          elif self.userMovies[movie] == -1: #they like the movie
            userGenresNeg[genre] += 1

      if userGenresPos: # make sure not empty
        mostPopGenre = max(userGenresPos, key=userGenresPos.get)
      if userGenresNeg: # make sure not empty
        leastPopGenre = max(userGenresNeg, key=userGenresNeg.get)

      if userGenresPos and userGenresPos[mostPopGenre] >= userGenresNeg[leastPopGenre] and userGenresPos[mostPopGenre] >= 2: #they had more of a fave than least fave
        return " I didn't know you love %s...interesting!" % mostPopGenre
      elif userGenresNeg and userGenresNeg[leastPopGenre] > userGenresPos[mostPopGenre] and userGenresNeg[leastPopGenre] >= 2: #they had more of a least fave than fave
        return " I'm not a fan of %s movies either." % leastPopGenre#mostPopGenre

      return ""


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
      CREATIVE EXTENSIONS
      1) Speaking Very Fluently
      2) Fine-Grained Sentiment - bot responds to certain strong words and intensifiers 
      2) Spell Checking Movie Titles
      3) Understanding references to things said previously (Note: this does not work for more than one movie)
      4) Extracting sentiment with multiple-movie input (two movie)
      5) Responding to arbitrary input (implementing- kevin)
      6) Identifying and Responding to Emotion (bot is great at identifying sadness, fear, anger, joy, and disgust but sometimes has a hard time differentiating amongst similar ones)

      OTHER CREATIVE FEATURES
      1) As a user starts telling Leroy about movies they like, he can pick up on their favorite or least favorite genres and let the user know. (must be at least 2 similar movie genres)
      2) Leroy will remember your name! Type: My name is ____ or I am ____
      3) User can get up to 5 movie recommendations
      4) Makes sure user is inputing new movies
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
