'''
Created on Dec 7, 2012

@author: Chris
Much of the NLP code was adapted from Mathew Russell's book Mining the Social Web
'''

import sys
print sys.path
import nltk
import json
from math import log
from pymongo import Connection
from pymongo.errors import ConnectionFailure



def main():
    
    """ Connect to MongoDB """
    try:
        c = Connection(host="localhost", port=27017)
        print "Connected successfully"
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
        
    #GET A DATABASE HANDLE TO A DATABASE CALLED play
    dbh = c["play"]
    assert dbh.connection == c
    print "Database handle successfully grabbed"
    
    #GRAB INFO FROM THE MONGO DATABASE
    apps = dbh.app.find()
    if not apps:
        print "No apps found" 
    else:
        print "Found %d apps" % apps.count()
        
    #GO THROUGH ALL OF THE APPS AND PUT THE DESCRIPTION IN A DICTIONARY
    app_description_corpus = {}
    query_scores = {}
    for app in apps:
        if not app.get("description"):
            print "No description for %s" % app.get("title")
            continue
        else:
            print "Title = %s" % app.get("title")
            description_string = app.get("description").encode('ascii','ignore')
            #print "Description = %s" % description_string
            
            #ELIMINATE THE STOPWORDS IN THE DESCRIPTION STRING
            description_string = drop_stopwords(description_string)
            app_description_corpus[app.get("title")] = description_string;
            query_scores[app.get("title")] = 0
    
    
    
    #QUERY_TERMS = sys.argv[1:] 
    term = "running"
    for doc in sorted(app_description_corpus):
        #print 'TF(%s): %s' % (doc, term), tf(term, doc)
        print 'TF(%s): %s' % (doc, term), tf(term, app_description_corpus[doc])
    
    print 'IDF: %s' % (term, ), idf(term, app_description_corpus.values())
    print
    
    for doc in sorted(app_description_corpus):
        score = tf_idf(term, app_description_corpus[doc], app_description_corpus.values())
        print 'TF-IDF(%s): %s' % (doc, term), score
        query_scores[doc] += score
    print
    
    
    
def drop_stopwords(doc):
                
    #GO THROUGH THE DESCIPTION AND DROP THE STOPWORDS
    tokens = doc.split()
    text = nltk.Text(tokens)
    fdist = text.vocab()
    print "Total words in description = %d" % len(tokens)
    print "Total unique words in description = %d" % len(fdist.keys())
    
    #REMOVE THE STOPWORDS FOR THE TOKENS
    go_words = [w for w in fdist.keys() \
        if w.lower() not in nltk.corpus.stopwords.words('english')]
    print "Total unique words less stopwords in description = %d" % len(go_words)            
    
    new_description = " ".join(tokens)
    return new_description
    
    #for rank, word in enumerate(go_words): 
    #    print rank, word, fdist[word]
                
def tf(term, doc, normalize=True):
    doc = doc.lower().split()
    if normalize:
        return doc.count(term.lower()) / float(len(doc))
    else:
        return doc.count(term.lower()) / 1.0

def idf(term, corpus):
    num_texts_with_term = len([True for text in corpus if term.lower() in text.lower().split()])

    #print "There are %d texts with the term" % num_texts_with_term
    #print "out of %d texts total" % len(corpus)
    #BECAUSE THE num_texts_with_term CAN BE 0 WE NEED TO BASE OUR CALCULATIONS AGAINST 1
    try:
        return 1.0 + log(float(len(corpus)) / num_texts_with_term)
    except ZeroDivisionError:
        return 1.0
    
def tf_idf(term, doc, corpus):
    return tf(term, doc) * idf(term, corpus)
    
if __name__ == '__main__':
    main()