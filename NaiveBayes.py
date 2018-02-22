#!/usr/bin/env python
# CS124 Homework 5 Jeopardy
# Original written in Java by Sam Bowman (sbowman@stanford.edu)
# Ported to Python by Milind Ganjoo (mganjoo@stanford.edu)

# This is a Naive Bayes implementation you can use.
# There's nothing for you to implement here, hooray!

import math
import itertools as it

class NaiveBayes:
    class ClassStats:
        def __init__(self):
            self.num_features = 0
            self.num_examples = 0
            self.counter = {}

        def log_likelihood(self, features, feature_set_size):
            prob = 0.0
            for feature in features:
                prob -= math.log(self.num_features + feature_set_size)
                prob += math.log(self.counter.get(feature, 0) + 1)
            return prob

    def __init__(self):
        """NaiveBayes initialization."""
        self.stats = {}
        self.feature_set = set()
        self.class_set = set()
        self.total_examples = 0

    def addExamples(self, features_list, labels):
        """Trains the model on some data. Simply call this with your labeled feature vectors (feature
        vectors and their corresponding labels must be in the same order) to train the model."""
        for features, label in it.izip(features_list, labels):
            self.addExample(label, features)

    def classify(self, features):
        """Returns a label for a set of features."""
        total_examples = 0
        for klass in self.class_set:
            total_examples = total_examples + self.stats[klass].num_examples
        log_total_examples = math.log(total_examples)

        probs = {}
        max_prob = float("-inf")
        for klass in self.class_set:
            probs[klass] = (self.stats[klass].log_likelihood(features, len(self.feature_set)) +
                    math.log(self.stats[klass].num_examples) - log_total_examples)
            max_prob = max(max_prob, probs[klass])

        for klass in self.class_set:
            if probs[klass] >= max_prob:
                return klass

        return "NO LABEL";

    @classmethod
    def crossValidate(self, features_list, labels):
        """Performs ten-fold cross validation on a set of labeled examples."""
        aggregate_score = 0.0
        NUM_FOLDS = 10

        # Make the folds.
        partition_size = float(len(labels)) / NUM_FOLDS
        label_partitions_list = []
        feature_partitions_list_list = []

        for i in xrange(NUM_FOLDS):
            start = int(math.floor(i * partition_size))

            if i == NUM_FOLDS - 1:
                end = len(labels)
            else:
                end = int(math.floor((i + 1) * partition_size))

            label_partitions_list.append(labels[start:end])
            feature_partitions_list_list.append(features_list[start:end])

        # Do crossvalidation.
        for i in xrange(NUM_FOLDS):
            training_features_list = []
            training_labels = []
            test_features_list = []
            test_labels = []
            for j in xrange(10):
                if j != i:
                    for fp in feature_partitions_list_list[j]:
                        training_features_list.append(fp)
                    for lp in label_partitions_list[j]:
                        training_labels.append(lp)
                else:
                    test_features_list = feature_partitions_list_list[j]
                    test_labels = label_partitions_list[j]

            nb = NaiveBayes()
            nb.addExamples(training_features_list, training_labels)
            score = nb.scoreData(test_features_list, test_labels)
            aggregate_score += score
            print "Fold {0} (train: {1} test: {2}) score: {3}".format(i, len(training_features_list),
                                                                        len(test_features_list), score)

        # Report overall score.
        print "Average score: {0}".format(aggregate_score / 10)
    
    def scoreData(self, features_list, labels):
        correct = 0
        for features, label in it.izip(features_list, labels):
            if self.classify(features) == label:
                correct += 1
        return float(correct) / len(labels)
    
    def addExample(self, klass, features):
        self.class_set.add(klass)
        if klass not in self.stats:
            self.stats[klass] = self.ClassStats()
        class_stat = self.stats[klass]
        
        class_stat.num_examples += 1
        for feature in features:
            self.feature_set.add(feature)
            if feature not in class_stat.counter:
                class_stat.counter[feature] = 0.0
            class_stat.counter[feature] += 1
            class_stat.num_features += 1

def main():
    """Run a simple test."""
    print "Testing the classifier..."

    good_features = []
    ok_features = []
    bad_features = []

    good_features.append("good")
    good_features.append("ok")

    ok_features.append("ok")
    ok_features.append("ok")
    ok_features.append("ok")
    ok_features.append("bad")

    bad_features.append("bad")
    bad_features.append("ok")

    labels = []
    labels.append("good-review")
    labels.append("ok-review")
    labels.append("bad-review")

    features = []
    features.append(good_features)
    features.append(ok_features)
    features.append(bad_features)

    nb = NaiveBayes()
    nb.addExamples(features, labels)

    test_features = []
    test_features.append("ok")
    test_features.append("ok")

    print "The test example 'ok ok' should be labeled 'ok-review', and is in fact labeled: {0}".format(nb.classify(test_features))

if __name__ == '__main__':
    main()
