# -*- coding: utf-8 -*-

import pandas as pd
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

movies_df = pd.read_csv("C:/Users/Adrija Guha/Downloads/movies.csv")
ratings_df = pd.read_csv("C:/Users/Adrija Guha/Downloads/ratings.csv")
#took out the year string from title
movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand = False)
movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand = False)
movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))','')
movies_df['title'] = movies_df['title'].apply(lambda x:x.strip())
#separated genres
movies_df['genres'] = movies_df.genres.str.split('|')
#trying to make a index so put genre = 1
movieswithgenres = movies_df.copy()
for index,row in movies_df.iterrows():
    for genre in row['genres']:
        movieswithgenres.at[index,genre] = 1
movieswithgenres = movieswithgenres.fillna(0)
#check out ratings
ratings_df= ratings_df.drop('timestamp',1)
#new user input to start recommendations
userInput = [
            {'title':'Breakfast Club, The', 'rating':5},
            {'title':'Toy Story', 'rating':3.5},
            {'title':'Jumanji', 'rating':2},
            {'title':"Pulp Fiction", 'rating':5},
            {'title':'Akira', 'rating':4.5}
            ]

inputmovies = pd.DataFrame(userInput)
#getting ids by title
inputid = movies_df[movies_df['title'].isin(inputmovies['title'].tolist())]
inputmovies = pd.merge(inputid,inputmovies)
inputmovies = inputmovies.drop('genres',1).drop('year',1)
#getting the input movies separately with all their original info
#so that we get to know the specific genre interest of user
usermovies  = movieswithgenres[movieswithgenres['movieId'].isin(inputmovies['movieId'].tolist())]

#Resetting the index to avoid future issues
usermovies = usermovies.reset_index(drop=True)
#Dropping unnecessary issues due to save memory and to avoid issues
userGenreTable = usermovies.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)

'''here we now have a beautiful only genre matrix what we need to judge to find interests of user
THIS INCLUDES MOVIES THAT ARE SEEN BY USER OR THE USER INPUT MOVIES hence step 1 
collected genre'''


#inputmovies['rating']
userProfile = userGenreTable.transpose().dot(inputmovies['rating'])

'''so userprofile is a cumulated list of sum of each genres for e.g.
Adventure             10.0
Animation              8.0
Children               5.5
Comedy                13.5
Fantasy                5.5
Romance                0.0
Drama                 10.0
Action                 4.5
Crime                  5.0'''

#Now let's get the genres of every movie in our original dataframe
genreTable = movieswithgenres.set_index(movieswithgenres['movieId'])
#And drop the unnecessary information
genreTable = genreTable.drop('movieId', 1).drop('title', 1).drop('genres', 1).drop('year', 1)
#Multiply the genres by the weights and then take the weighted average sort of the normalisation
#of the genreTable
recommendationTable_df = ((genreTable*userProfile).sum(axis=1))/(userProfile.sum())

#Sort our recommendations in descending order
#of course so that u get the highest rated movies the first
recommendationTable_df = recommendationTable_df.sort_values(ascending=False)

#The final recommendation table
movies_df.loc[movies_df['movieId'].isin(recommendationTable_df.head(20).keys())]


















