#!/usr/bin/env python

#  Author: Angela Chapman
#  Date: 8/6/2014
#
#  This file contains code to accompany the Kaggle tutorial
#  "Deep learning goes to the movies".  The code in this file
#  is for Parts 2 and 3 of the tutorial, which cover how to
#  train a model using Word2Vec.
#
# *************************************** #


# ****** Read the two training sets and the test set
#
import pandas as pd
import os
from nltk.corpus import stopwords
import nltk.data
import logging
import numpy as np  # Make sure that numpy is imported
from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier

from KaggleWord2VecUtility import KaggleWord2VecUtility
import sys
import time
import json
from sklearn.preprocessing import Imputer
from collections import defaultdict

# ****** Define functions to create average word vectors
#

def makeFeatureVec(words, model, num_features):
    # Function to average all of the word vectors in a given
    # paragraph
    #
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((num_features,),dtype="float32")
    #
    nwords = 0.
    #
    # Index2word is a list that contains the names of the words in
    # the model's vocabulary. Convert it to a set, for speed
    index2word_set = set(model.index2word)
    #
    # Loop over each word in the review and, if it is in the model's
    # vocaublary, add its feature vector to the total
    for word in words:
        if word in index2word_set:
            nwords = nwords + 1.
            featureVec = np.add(featureVec,model[word])
    #
    # Divide the result by the number of words to get the average
    featureVec = np.divide(featureVec,nwords)
    return featureVec


def getAvgFeatureVecs(reviews, model, num_features):
    # Given a set of reviews (each one a list of words), calculate
    # the average feature vector for each one and return a 2D numpy array
    #
    # Initialize a counter
    counter = 0.
    #
    # Preallocate a 2D numpy array, for speed
    reviewFeatureVecs = np.zeros((len(reviews),num_features),dtype="float32")
    #
    # Loop through the reviews
    for review in reviews:
       #
       # Print a status message every 1000th review
       #
       # Call the function (defined above) that makes average feature vectors
       reviewFeatureVecs[counter] = makeFeatureVec(review, model, \
           num_features)
       #
       # Increment the counter
       counter = counter + 1.
    return reviewFeatureVecs


def getCleanReviews(reviews):
    clean_reviews = []
    for review in reviews:
        clean_reviews.append( KaggleWord2VecUtility.review_to_wordlist( review, remove_stopwords=True ))
    return clean_reviews



if __name__ == '__main__':

    # Read data from files
    input1=sys.argv[1]
    #input2=sys.argv[2]
    input3=sys.argv[2]
    
    O_train=json.load(open(input1))
    #O_test=json.load(open(input2))
    tag_dic=json.load(open(input3))
    
    train=[]
    test=[]
    tag=defaultdict()
    Y=[]

    c=0
    for i in O_train:
        train.append(O_train[i][1])
        for j in O_train[i][3].split():
            if j in tag_dic:
               if c not in tag:
                  tag[c]=[]
               else:
                  tag[c].append(tag_dic[j])
        c+=1
        
    for x in range(len(tag)):
        if x in tag:
           Y.append(tag[x])

#for i in O_test:
#test.append(O_test[i][0])

    # Load the punkt tokenizer
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # ****** Split the labeled and unlabeled training sets into clean sentences
    #
    sentences = []  # Initialize an empty list of sentences

#print("Parsing sentences from training set")
    for review in train:
        sentences += KaggleWord2VecUtility.review_to_sentences(review.encode('utf-8'), tokenizer)

# print "Parsing sentences from training set"
        #for review in test:
# sentences += KaggleWord2VecUtility.review_to_sentences(review, tokenizer)

    # ****** Set parameters and train the word2vec model
    #
    # Import the built-in logging module and configure it so that Word2Vec
    # creates nice output messages
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
        level=logging.INFO)

    # Set values for various parameters
    num_features = 300    # Word vector dimensionality
    min_word_count = 40   # Minimum word count
    num_workers = 4       # Number of threads to run in parallel
    context = 10          # Context window size
    downsampling = 1e-3   # Downsample setting for frequent words

    # Initialize and train the model (this will take some time)
    print ("Training Word2Vec model...")
    start_time3 = time.time()
    model = Word2Vec(sentences, workers=num_workers, \
                size=num_features, min_count = min_word_count, \
                window = context, sample = downsampling, seed=1)
    print("--- %s seconds ---" % (time.time() - start_time3))

    # If you don't plan to train the model any further, calling
    # init_sims will make the model much more memory-efficient.
    model.init_sims(replace=True)

    # It can be helpful to create a meaningful model name and
    # save the model for later use. You can load it later using Word2Vec.load()
    model_name = "300features_40minwords_10context"
    model.save(model_name)

    #model = Word2Vec.load(fname)

# model.doesnt_match("man woman child kitchen".split())
#   model.doesnt_match("france england germany berlin".split())
#   model.doesnt_match("paris berlin london austria".split())
#    model.most_similar("I")


# ****** Create average vectors for the training and test sets
#
    print ("Creating average feature vecs for training reviews")

    trainDataVecs = getAvgFeatureVecs( getCleanReviews(train), model, num_features )

    print ("Creating average feature vecs for test reviews")

# testDataVecs = getAvgFeatureVecs( getCleanReviews(test), model, num_features )
    testDataVecs=trainDataVecs

    trainDataVecs = Imputer().fit_transform(trainDataVecs)
# ****** Fit a random forest to the training set, then make predictions
#
# Fit a random forest to the training data, using 100 trees
    forest = RandomForestClassifier( n_estimators = 100 )

    print ("Fitting a random forest to labeled training data...")
    
    forest = forest.fit( trainDataVecs, Y )

# Test & extract results
    result = forest.predict( testDataVecs )

# Write the test results
    for y in result:
        print(y)
