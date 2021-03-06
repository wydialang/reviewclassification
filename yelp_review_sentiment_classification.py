# -*- coding: utf-8 -*-
"""Yelp_Review_Sentiment_Classification.ipynb


# Yelp Review Sentiment Classification

building a classifier that can predict a user's rating of a given restaurant from their review

![Example of a Yelp review](https://wordstream-files-prod.s3.amazonaws.com/s3fs-public/styles/simple_image/public/images/yelp-reviews-filtered.png)
"""

#@title Import libraries 
import pandas as pd   # note great for tables (google spreadsheets, microsoft excel, csv). 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import string
import nltk
import spacy
import wordcloud
import os # for navigating your computer's files 
import sys

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from spacy.lang.en.stop_words import STOP_WORDS
nltk.download('wordnet')
nltk.download('punkt')

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
!python -m spacy download en_core_web_md
import en_core_web_md

#@title Import data

import gdown
gdown.download('https://drive.google.com/uc?id=1u0tnEF2Q1a7H_gUEH-ZB3ATx02w8dF4p', 'yelp_final.csv', True)
data_file  = 'yelp_final.csv'

"""## Data Exploration

read in the file containing the reviews and take a look at the data available.
"""

# read data in using 'pd.read_csv('file')'
yelp = pd.read_csv(data_file)

#@title Show data
yelp.head()

"""

hashing (https://medium.com/tech-tales/what-is-hashing-6edba0ebfa67).
"""

#@title **Run to remove unnecessary columns** { display-mode: "form" }
yelp.drop(labels=['business_id','user_id'],inplace=True,axis=1)

"""The text column is the one we are primarily focused with. Let's take a look at a few of these reviews to better understand our problem."""

#@title Check the text in differently rated reviews
num_stars =  1#@param {type:"integer"}

for t in yelp[yelp['stars'] == num_stars]['text'].head(20).values:
    print (t)

"""

"""

#@title Rules
rule_1 = "bad" #@param {type:"string"}
rule_2 = "" #@param {type:"string"}
rule_3 = "" #@param {type:"string"}

"""It is not really the presence of individual words that gives an indication of the stars given to a review, but more  the *relative occurrence* of these words in each review 

#### Word Clouds
"""

#@title Word cloud for differently rated reviews
num_stars =  1#@param {type:"integer"}
this_star_text = ''
for t in yelp[yelp['stars'] == num_stars]['text'].values: # form field cell
    this_star_text += t + ' '
    
wordcloud = WordCloud()    
wordcloud.generate_from_text(this_star_text)
plt.figure(figsize=(14,7))
plt.imshow(wordcloud, interpolation='bilinear')

"""**What are the differences between the reviews that have 1, 2, 3, 4, and 5 stars?**


## Text Preprocessing

#### Tokenization

"""

#@title Basic tokenization example
example_text = "All the people I spoke to were super nice and very welcoming." #@param {type:"string"}
tokens = word_tokenize(example_text)
tokens

"""#### Stopwords

"""

#@title Check if a word is a stop word
example_word = "the" #@param {type:'string'}
if example_word.lower() in STOP_WORDS:
  print (example_word + " is a stop word.")
else:
  print (example_word + " is NOT a stop word.")

"""


# Intro to Spacy




`
nlp = spacy.load('en_core_web_md')
`


explore Spacy 
"""

nlp = en_core_web_md.load()
doc = nlp(u"We are running out of time! Are we though?")
doc

"""you can get the text of each of the words and the length of each of the words"""

doc = nlp(u"We are running out of time! Are we though?")
token = doc[0] # Get the first word in the text.
assert token.text == u"We" # Check that the token text is 'We'.
assert len(token) == 2 # Check that the length of the token is 2.

"""import a new dataset of word:

We can get the word embedding of a particular word in our document as follows:
"""

doc = nlp(u"I like apples")
print(doc)
appleVariable = doc[2]

print(appleVariable.vector) # Each word is being represented by 300 dimensional vector embedding

"""The word 'Apple' is represented by 300 dimensional vector embedding

### Fun things you can do with word vectors

### 

You can get the similarity of two words via the following method:


```
doc = nlp(u"keyboard and mouse")
word1 = doc[0]
word2 = doc[2]
word1.similarity(word2)
```

**Use the above methodology to find two words with a similarity greater than 0.77 and two words with similarity less than 0.15. **
"""

### YOUR CODE HERE
doc = nlp(u"bird and disapperance")
word1 = doc[0]
word2 = doc[2]
word1.similarity(word2)
### END CODE

#@title Sample instructor solution { display-mode: "form" }
similar_words_doc = nlp(u"apples oranges")
w1 = similar_words_doc[0]
w2 = similar_words_doc[1]
print(w1.similarity(w2))

dissimilar_words_doc = nlp(u"doorknob phone")
w3 = dissimilar_words_doc[0]
w4 = dissimilar_words_doc[1]
print(w3.similarity(w4))

"""the language in 4 star reviews is quite similar to the language in 5 star reviews. So the text in those reviews might not be very useful and we can drop those rows from our data.

Although the text in the 3 star reviews is not very similar to the 1 or 2 star reviews, it is quite different from the language used in the 5 star reviews. 
In order to reduce our problem to a **binary classification** problem, we will:

 - remove all 4 star reviews
 - label 5 star reviews as 'good'
 - label 1, 2, 3 star reviews as 'bad'

Run the cell below to get rid of 4 star reviews.
"""

yelp = yelp[yelp.stars != 4]

"""### Exercise 3

Complete the second line of code in the cell below, and run it to re-categorize reviews.
"""

def is_good_review(stars):
    if _____: ### TODO: FILL IN THE IF STATEMENT HERE ###
        return True
    else:
        return False

# Change the stars field to either be 'good' or 'bad'.
yelp['is_good_review'] = yelp['stars'].apply(is_good_review)

#@title Solution hidden { display-mode: "form" }
def is_good_review(stars):
    if stars > 3:             
        return True
    else:
        return False
    
yelp['is_good_review'] = yelp['stars'].apply(is_good_review)
yelp.head()

"""## One-Hot Vectors

How do we convert our text to numbers in a structured way that we can feed into a machine learning algorithm? "one-hot encoding"!!! 
"""

#@title Run this to see the one-hot encoding of 'great tacos at this restaurant'
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('great', 'tacos', 'at','this','restaurant'))
print('--------------------------------------------')
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('1', '0', '0','0','0'))
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('0', '1', '0','0','0'))
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('0', '0', '1','0','0'))
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('0', '0', '0','1','0'))
print('{:^5}|{:^5}|{:^4}|{:^4}|{:^10}'.format('0', '0', '0','0','1'))

"""###Exercise: One Hot Encoding - Sentences

Let's say you just have two reviews(vocabulary) as following:

1. I loved the restaurant
2. I hate the food 

The vocabulary would consist of unique words across both the reviews. Now create one-hot encoded vector for reviews above. (No coding needed).
"""

#@title Solution

#Unique Vocab - ['I','loved','the','restaurant','hate','food']
#One Hot Encoding - 1st - [1,1,1,1,0,0] , 2nd - [1,0,1,0,1,1]

"""## Bag of Words

Building upon the concept of one-hot encoding is the **bag of words** model. If one-hot encoding is a way to represent individual words as vectors, then you can think of bag of words as a way to represent sentences (or larger pieces of text) as the **sum** of the one-hot encoding vectors of each of the words. Let's explain with an example. 

Suppose we want to represent the review: 
**"The food was great. The ambience was also great."** as a bag of words.

First we define our vocabulary. This is *each unique word* in the review. So our vocabulary is **[the, food, was, great, ambience, also]**.

What are our one hot encodings? 

the = (1,0,0,0,0,0)

food = (0,1,0,0,0,0)

was = (0,0,1,0,0,0)

great = (0,0,0,1,0,0)

ambience = (0,0,0,0,1,0)

also = (0,0,0,0,0,1).

So far, so simple. Now how do we represent the review we mentioned above as a bag of words? We know we only have 6 words in our vocabulary, so our bag of words vector will also only be 6 elements long. To construct it, we can start off with a (0,0,0,0,0,0) vector, and then pass through each word in the review. For each word we encounter, we simply add its one hot encoding to our vector! So for our review, the bag of words representation will be

**(2,1,2,2,1,1)**

## Creating our Bag of Words

Back to our data. We want to select the features for our model and the output classes from our data. What are the features? We are only using the review text to make predictions for our model. And the output classes are the 'good' and 'bad' review classes we created just above. 

By convention, we represent our entire set of features as X, and our target output as y. Running the cell below will create the relevant X and y for our problem.
"""

X = yelp['text']
y = yelp['is_good_review']

"""Running the cell below will create an object we can use to *transform* each piece of raw text into a bag of words vector.
CountVectorizer is a useful class we can call from scikit-learn that will help us create this object. It even has a helpful parameter that we can set to our tokenize function to preprocess the raw text.
"""

#@title Initialize the text cleaning function { display-mode: "form" }
def tokenize(text):
    clean_tokens = []
    for token in nlp(text):
        if (not token.is_stop) & (token.lemma_ != '-PRON-') & (not token.is_punct): # -PRON- is a special all inclusive "lemma" spaCy uses for any pronoun, we want to exclude these 
            clean_tokens.append(token.lemma_)
    return clean_tokens

bow_transformer = CountVectorizer(analyzer=tokenize, max_features=1600).fit(X)

"""We can see our entire vocabulary by running the cell below! You will also notice an index associated with each word - this is the position of each word in the vocabulary."""

bow_transformer.vocabulary_

"""We can see the length of the vocabulary stored in the transformer object by running the cell below."""

len(bow_transformer.vocabulary_)

"""Finally, to finish preparing our data, we can use the transformer to transform our entire training set (X) into a series of bag of words vectors:"""

X = bow_transformer.transform(X)

"""## Training a Baseline Classification Model (Logistic Regression)

Our classification problem is a classic two-class classification problem, and so we will use the tried and tested **Logistic Regression** machine learning model from yesterday's class.
"""

# import the logistic regression model from scikit-learn
logistic_model = LogisticRegression()

"""We will use 20% of our data as test data. If you run the cell below, it will randomly split the data such that 80% of it is training data and 20% of it is data we can use to test the predictions from our trained model."""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)

"""### 
train our model. 
"""

### YOUR CODE HERE

### END CODE

#@title Solution hidden { display-mode: "form" }
logistic_model.fit(X_train, y_train)

"""## Exercise 5

Once the model is trained, we can generate predictions from our test data. Just like the fit() function above, there is a similar predict() function that we can use once our model is trained. Create your model's predictions on the text model. Next, use the true positive (TP), false positive (FP), true negative (TN), and false negative (FN) rates to evaluate the accuracy of the model.
"""

### YOUR CODE HERE

preds = ###

# Get the confusion matrix.
cm = confusion_matrix(y_test, preds)

# Get TP, FP, TN, and FN rates.
TP = cm[0][0]
TN = cm[1][1]
FP = cm[0][1]
FN = cm[1][0]

accuracy = ### 

print("The accuracy of the model is " + str(accuracy*100) + "%")

### END CODE

#@title Solutions hidden.

# Get our predictions.
preds = logistic_model.predict(X_test)

# Get the confusion matrix.
cm = confusion_matrix(y_test, preds)

# Get TP, FP, TN, and FN rates.
TP = cm[0][0]
TN = cm[1][1]
FP = cm[0][1]
FN = cm[1][0]

# Calculate and print accuracy.
accuracy = (TP + TN)/(TP + TN + FP + FN)
print ("The accuracy of the model is " + str(accuracy*100) + "%")

"""Not perfect, but definitely better than we would have expected at random (50%).

Enter an example review to see if our model predicts it as a positive one or a negative one.
"""

#@title Enter an example review, and see if it is classified as good or bad
example_review = "good!!!!!!!!!!!!!" #@param {type:'string'}
prediction = logistic_model.predict(bow_transformer.transform([example_review]))

if prediction:
  print ("This was a GOOD review!")
else:
  print ("This was a BAD review!")

"""###Exercise 6

Now change the max features attribute while creating your bag of words model. Discuss how the change affects the accuracy of the model

###Exercise 7 (Optional)
We used Logistic regression for our baseline model. However we could also use a separate model called Multinomial Naive Bayes to perform our classification.
Naive Bayes uses Bayes' Theorem of probability to predict class of new input data. The important assumption Naive Bayes makes is that the presence of one feature is independent of the presence of any other.

Let's build a model using a Naive Bayes classifier!
"""

from sklearn.naive_bayes import MultinomialNB
nb_model = MultinomialNB()

"""We can train and generate predictions from this model in the same way we did for our Logistic Regression model. Try training this model on the same data and see if it performs better or worse than our logistic regression model. Then, evaluate the model accuracy as your did for the Logistic Regression classifier."""

###YOUR CODE HERE####

#@title Solution hidden
nb_model.fit(X_train, y_train)
nb_preds = nb_model.predict(X_test) 
nbcm = confusion_matrix(y_test, nb_preds)
accuracy = (nbcm[0][0] + nbcm[1][1])/(nbcm[0][0] + nbcm[0][1] + nbcm[1][0]+ nbcm[1][1])
print ("The accuracy of the model is " + str(accuracy*100) + "%")

"""Experiment with the models you've learned so far and try to get the highest accuracy!"""

###YOUR CODE HERE###

"""### Exercise 8

We saw earlier that our WordClouds didn't give us too much useful information. What words were present across all kinds of reviews? If we take those words out of the reviews, we could possibly have more useful WordClouds.

Identify some of these common words and add them to the list in the cell below. Then, run the word cloud to see the words that show up across review types.
"""

###Fill in the list with the words you think which should be removed. Ex: ['food','time','service']###
common_words = ["food", "time", "good", "place", "one", "us", "even", "will", "jt"]

#@title Solution
common_words = ['got','will','go','even','food','service',
                 'place','restuarant','good','one','really',
                 'time','back','review','customer','order']

#@title Word cloud for differently rated reviews
num_stars =  2#@param {type:"integer"}
this_star_text = ''
for t in yelp[yelp['stars'] == num_stars]['text'].values: # form field cell
    this_star_text += t + ' '
    for word in common_words:
      this_star_text = this_star_text.replace(word,'')
    
wordcloud = WordCloud()    
wordcloud.generate_from_text(this_star_text)
plt.figure(figsize=(14,7))
plt.imshow(wordcloud, interpolation='bilinear')

"""### (Optional Advanced Exercise) Training Logistic Regression with Word Vectors from Spacy

We can use the word vectors we introduced earlier to get more sophisticated representations of our Yelp reviews. First, we get the text data from our dataframe:
"""

X_data = yelp['text']
y_data = yelp['is_good_review']

"""This helper function uses the Spacy `nlp` object to remove stop words, pronouns, and punctuation. It is identical to the `tokenize` function above, except it preserves the non-string attributes of the clean tokens (i.e. `token.vector`)"""

def tokenize_vecs(text):
    clean_tokens = []
    for token in nlp(text):
        if (not token.is_stop) & (token.lemma_ != '-PRON-') & (not token.is_punct): 
          # -PRON- is a special all inclusive "lemma" spaCy uses for any pronoun, we want to exclude these 
            clean_tokens.append(token)
    return clean_tokens

"""We want to represent each Yelp review with a vector. Since each review consists of multiple words, we want to find a way to create one vector for each review. 

Would adding the word vectors work? What about averaging? Which would be preferrable?

Implement your solution below: convert our array of reviews into an array of vector representations of those reviews.
"""

X_word2vec = []
for text in X_data:
  review = tokenize_vecs(text) # returns cleaned list of spacy tokens
  #### YOUR CODE HERE
  
  
  #### END CODE
  
X_word2vec = np.array(X_word2vec)

#@title Instructor Solution (Uses Mean of Word Vectors)

X_word2vec = []
for text in X_data:
  review = tokenize_vecs(text) # returns cleaned list of spacy tokens
  review_vec = 0
  for word in review:
    review_vec += word.vector
  review_vec = review_vec / len(review)
  X_word2vec.append(review_vec)

X_word2vec = np.array(X_word2vec)

"""Now we follow the same procedure for training and testing the logistic regression that we used for the Bag of Words data."""

# import a fresh logistic regression model from scikit-learn
logistic_model = LogisticRegression()

# train-test split
X_train_word2vec, X_test_word2vec, y_train_word2vec, y_test_word2vec = train_test_split(X_word2vec, y, test_size=0.2, random_state=101)

logistic_model.fit(X_train_word2vec, y_train_word2vec)

#@title Run this to print the accuracy for our word2vec classifier


# Get our predictions.
preds = logistic_model.predict(X_test_word2vec)

# Get the confusion matrix.
cm = confusion_matrix(y_test_word2vec, preds)

# Get TP, FP, TN, and FN rates.
TP = cm[0][0]
TN = cm[1][1]
FP = cm[0][1]
FN = cm[1][0]

# Calculate and print accuracy.
accuracy = (TP + TN)/(TP + TN + FP + FN)
print ("The accuracy of the model is " + str(accuracy*100) + "%")

"""For Instructors: Target Accuracy = 76.15384615384615%

### Challenge Exercise: Calculating Similarity and Analogies

Once we have text embeddings, we can use them to explore connections in meaning between different words, including calculating similarity between words and completing analogies.

We'll start by creating a dictionary containing the vectors for all the words in our vocabulary. We'll stick to the vocabulary above of 800 words from the Yelp reviews - if you want to use more words, change that number!
"""

vocab_dict = dict() #initialize dictionary

for word in bow_transformer.vocabulary_:
    vocab_dict[word] = nlp(word).vector #what is the key? what is the value?

for word, vec in vocab_dict.items(): #iterating through the dictionary to print each key and value
  print ('Word: {}. Vector length: {}'.format(word, len(vec)))

print()
print ('{} words in our dictionary'.format(len(vocab_dict)))

"""Next, let's calculate the similarity between two words, using their Word2Vec representations.

A common way to calculate the similarity between two vectors is called *cosine similarity*. It depends on the angle between those two vectors when plotted in space. As an example, imagine we had two three-dimensional vectors:
"""

v0 = [2,3,1]
v1 = [-2,-3,-1]

"""Run the code below to plot those vectors, and try changing the numbers above.
How can you make a very small angle between the vectors? How can you make a very large angle?
"""

#@title Run this to create an interactive 3D plot
#Code from https://stackoverflow.com/questions/47319238/python-plot-3d-vectors 
import numpy as np 
import plotly.graph_objs as go

def vector_plot(tvects,is_vect=True,orig=[0,0,0]):
    """Plot vectors using plotly"""

    if is_vect:
        if not hasattr(orig[0],"__iter__"):
            coords = [[orig,np.sum([orig,v],axis=0)] for v in tvects]
        else:
            coords = [[o,np.sum([o,v],axis=0)] for o,v in zip(orig,tvects)]
    else:
        coords = tvects

    data = []
    for i,c in enumerate(coords):
        X1, Y1, Z1 = zip(c[0])
        X2, Y2, Z2 = zip(c[1])
        vector = go.Scatter3d(x = [X1[0],X2[0]],
                              y = [Y1[0],Y2[0]],
                              z = [Z1[0],Z2[0]],
                              marker = dict(size = [0,5],
                                            color = ['blue'],
                                            line=dict(width=5,
                                                      color='DarkSlateGrey')),
                              name = 'Vector'+str(i+1))
        data.append(vector)

    layout = go.Layout(
             margin = dict(l = 4,
                           r = 4,
                           b = 4,
                           t = 4)
                  )
    fig = go.Figure(data=data,layout=layout)
    fig.show()


vector_plot([v0,v1])

"""For our Word2Vec vectors, we can imagine doing the same thing in 300-dimensional space. Of course, it's much harder to plot that! [Here](https://projector.tensorflow.org/) is one representation that you can play around with.

Then we find the cosine of the angle between the two vectors to get the similarity. 

If the vectors are exactly the same, the angle will be 0, so we get a similarity of cos(0) = 1.

If the vectors are exactly opposite, the angle will be 180 degrees, so we get a similarity of cos(180) = -1.

There's a useful [mathematical trick](https://www.mathsisfun.com/algebra/vectors-dot-product.html) to find the cosine similarity:

![](https://wikimedia.org/api/rest_v1/media/math/render/svg/1d94e5903f7936d3c131e040ef2c51b473dd071d)

Where A_1, A_2, ..., A_300 are the elements of the first vector and B_1, B_2, ..., B_300 are the elements of the second vector.

Please implement cosine similarity below, and test it out using our 3-dimensional vectors from above. Do the results make sense?
"""

def vector_cosine_similarity(vec1,vec2):
  #Assume vec1 and vec2 have the same size 

  #YOUR CODE HERE

  return similarity #number between -1 and 1

print(vector_cosine_similarity(v0,v1))

#@title Instructor Solution
def vector_cosine_similarity(vec1,vec2):
  #Assume vec1 and vec2 have the same size 

  #YOUR CODE HERE
  numerator = 0
  for i in range(len(vec1)):
    numerator += vec1[i]*vec2[i]
  mag1 = (sum(elem**2 for elem in vec1))**0.5
  mag2 = (sum(elem**2 for elem in vec2))**0.5
  similarity = numerator/(mag1*mag2)
  return similarity

print(vector_cosine_similarity(v0,v1))

"""Now, use your cosine similarity function to calculate the similarity between two words. Try out a few words from the dataset - what pairs of words can you find that are particularly similar or particularly dissimilar?"""

def word_similarity(word1, word2):
  #Should return a similarity between -1 and 1
  
  try:
    vec1 = vocab_dict[word1]
    vec2 = vocab_dict[word2]

    #TODO: Fill in the return statement here

  except KeyError:
    print ('Word not in dictionary')

print(word_similarity('burger','steak'))

#@title Instructor Solution
def word_similarity(word1, word2):
  #Should return a similarity between -1 and 1
  
  try:
    vec1 = vocab_dict[word1]
    vec2 = vocab_dict[word2]
    return vector_cosine_similarity(vec1,vec2)

  except KeyError:
    print ('Word not in dictionary')

print(word_similarity('burger','steak'))

"""Now, we can use our functions above to find the *most* similar words to any particular word. 

`find_most_similar(start_vec)` should output the top 5 words whose vectors are most similar to start_vec, with their similarities. Please fill it in.
"""

def find_nearest_neighbor(word):
  try:
    vec = vocab_dict[word]
    find_most_similar(vec)
  except KeyError:
    print ('Word not in dictionary')

def find_most_similar(start_vec):
  #Should print the top 5 most similar words to start_vec, and their similarities.,
  #Hint: use a for loop to iterate through vocab_dict.
  #Consider using a Pandas series.

  #YOUR CODE HERE
  print (five_most_similar) #words and similarities

find_nearest_neighbor('bagel')

#@title Instructor Solution
def find_nearest_neighbor(word):
  try:
    vec = vocab_dict[word]
    find_most_similar(vec)
  except KeyError:
    print ('Word not in dictionary')

def find_most_similar(start_vec):
  #Should print the top 5 most similar words to start_vec, and their similarities.,
  #Hint: use a for loop to iterate through vocab_dict.
  #Consider using a Pandas series.

  #YOUR CODE HERE
  similarity_series = pd.Series(np.nan, index = vocab_dict.keys())
  for word, vec in vocab_dict.items():
    similarity_series[word] = vector_cosine_similarity(start_vec, vec)
  similarity_series = similarity_series[similarity_series.notna()] #get rid of N/A
  five_most_similar = similarity_series.sort_values().tail()
  print (five_most_similar) #words and similarities

find_nearest_neighbor('bagel')

"""Finally, we can use the functions we've built to complete word analogies, like the ones you can try out [here](http://bionlp-www.utu.fi/wv_demo/). For example:

*   Guacamole is to Mexican as pasta is to ________,

This requires a bit of "word arithmetic":
let's say A1, A2, and B1 are vectors for three words we know. We're trying to find B2 to complete 

*   A1 is to A2 as B1 is to B2.

Intuitively, this means that the difference between A1 and A2 is the same as the difference between B1 and B2. So we write

*   A1 - A2 = B1 - B2

**Solve for B2:**

*   B2 = ________________

Once we know the vector that we "expect" for B2, we can use our previous functions to find the word whose representation is closest to that vector. Try it out!
"""

def find_analogy(word_a1, word_a2, word_b1):
  #Convert the words to vectors a1, a2, b1
  #If word_a1:word_a2 as word_b1:word_b2, then 
  #a1 - a2 = b1 - b2
  #So b2 = ...
  #Calculate b2, and use your previous functions to find the best candidates for word_b2.

  #YOUR CODE HERE

find_analogy('guacamole','mexican','pasta')

#@title Instructor Solution
def find_analogy(word_a1, word_a2, word_b1):
  #Convert the words to vectors a1, a2, b1
  #If word_a1:word_a2 as word_b1:word_b2, then 
  #a1 - a2 = b1 - b2
  #So b2 = ...
  #Calculate b2, and use your previous functions to find the best candidates for word_b2.

  #YOUR CODE HERE
  a1_vec = vocab_dict[word_a1]
  a2_vec = vocab_dict[word_a2]
  b1_vec = vocab_dict[word_b1]
  find_most_similar(b1_vec - a1_vec + a2_vec)

find_analogy('guacamole','mexican','pasta')

"""Word arithmetic doesn't always work perfectly - it's pretty tricky to find good examples! Which can you discover?

If you're looking for a way to expand further on this exercise, you can try seeing what happens when you use [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance), another common measurement, instead of cosine similarity.
"""
