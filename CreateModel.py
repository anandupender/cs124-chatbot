import math
import itertools as it

from NaiveBayes import NaiveBayes
import glob   
import os


class CreateModel:
    def __init__(self):
        self.classifier = NaiveBayes()
        self.stop_words = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}


    def train(self, file, klass):
        """Trains the model on clues paired with gold standard parses."""

        features = []
        for line in file:
            for word in line.split(' '):
                # if word not in self.stop_words:
                features.append(word)
        self.classifier.addExample(klass, features)

        # def train(self, clues, parsed_clues):
        # """Trains the model on clues paired with gold standard parses."""
        # all_features = []
        # all_klasses = []
        # features_list = []
        # for clue,parsed_clue in zip(clues,parsed_clues):
        #     features_list = self.feature_extractor(clue)
        #     all_features.append(features_list)
        #     all_klasses.append(parsed_clue.split(':')[0])
        # self.classifier.addExamples(all_features, all_klasses)

    def classifyTest(self,user_input):
        return self.classifier.classify(user_input)


def main():
    """Tests the model on the command line. This won't be called in
        scoring, so if you change anything here it should only be code 
        that you use in testing the behavior of the model."""

    cm = CreateModel()

    path2 = 'imdb1/pos'   
    listing2 = os.listdir(path2)
    for file2 in listing2:
        print "current file is: " + file2
        f2 = open(path2+"/"+file2,'r')
        # for line2 in f2:
        # toSend = self.readFile('%s/pos/%s' % (trainDir, fileName))

        cm.train(f2,"pos")

    path1 = 'imdb1/neg'   
    listing = os.listdir(path1)
    for file in listing:
        print "current file is: " + file
        f = open(path1+"/"+file,'r')
        # for line in f:
        cm.train(f,"neg")


    # path1 = 'data'   

    # f = open("data/sentiment.txt",'r')
    # for line in f:
    #     text = line.split(",")
    #     text[1] = text[1][0:len(text) - 4]
    #     print text
    #     cm.train(text[0],text[1])

    string = "an interesting movie"
    string = string.split(" ")
    guess = cm.classifyTest(string)
    print guess

if __name__ == '__main__':
    main()