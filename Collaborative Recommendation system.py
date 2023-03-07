# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 19:03:57 2022

@author: Adrija Guha
"""

import pandas as pd
import numpy as np
from math import sqrt

movies_df = pd.read_csv("C:/Users/Adrija Guha/Downloads/movies.csv")
ratings_df = pd.read_csv("C:/Users/Adrija Guha/Downloads/ratings.csv")

movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand = False)
movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand = False)
movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))','')
movies_df['title'] = movies_df['title'].apply(lambda x:x.strip())

movies_df = movies_df.drop('genres',1)

ratings_df = ratings_df.drop('timestamp',1)

'''                           USER BASED RECOMMENDER SYSTEM                   '''
userInput = [
            {'title':'Breakfast Club, The', 'rating':5},
            {'title':'Toy Story', 'rating':3.5},
            {'title':'Jumanji', 'rating':2},
            {'title':"Pulp Fiction", 'rating':5},
            {'title':'Akira', 'rating':4.5}
         ] 

inputmovies_df = pd.DataFrame(userInput)
inputId = movies_df[movies_df['title'].isin(inputmovies_df['title'].tolist())]
inputmovies_df = pd.merge(inputId,inputmovies_df)
inputmovies_df = inputmovies_df.drop('year',1)

usersubset = ratings_df[ratings_df['movieId'].isin(inputmovies_df['movieId'].tolist())]

usergroupsubset = usersubset.groupby(['userId'])

# NOT WORKING !!!!!!! usergroupsubset.get_group(1130)
usergroupsubset = sorted(usergroupsubset,key=lambda x:len(x[1]),reverse = True)
usergroupsubset[0:3]
usergroupsubset = usergroupsubset[0:100]


#Store the Pearson Correlation in a dictionary, where the key is the user Id and the value is the coefficient
pearsonCorrelationDict = {}

#For every user group in our subset
for name, group in usergroupsubset:
    #Let's start by sorting the input and current user group so the values aren't mixed up later on
    group = group.sort_values(by='movieId')
    inputmovies_df = inputmovies_df.sort_values(by='movieId')
    #Get the N for the formula
    nRatings = len(group)
    #Get the review scores for the movies that they both have in common
    temp_df = inputmovies_df[inputmovies_df['movieId'].isin(group['movieId'].tolist())]
    #And then store them in a temporary buffer variable in a list format to facilitate future calculations
    tempRatingList = temp_df['rating'].tolist()
    #Let's also put the current user group reviews in a list format
    tempGroupList = group['rating'].tolist()
    #Now let's calculate the pearson correlation between two users, so called, x and y
    Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
    Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
    Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)
    
    #If the denominator is different than zero, then divide, else, 0 correlation.
    if Sxx != 0 and Syy != 0:
        pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
    else:
        pearsonCorrelationDict[name] = 0


pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
pearsonDF.columns = ['similarityIndex']
pearsonDF['userId'] = pearsonDF.index
pearsonDF.index = range(len(pearsonDF))
pearsonDF.head()

topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]
topUsersRating=topUsers.merge(ratings_df, left_on='userId', right_on='userId', how='inner')

topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']


tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']


#Creates an empty dataframe
recommendation_df = pd.DataFrame()
#Now we take the weighted average
recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
recommendation_df['movieId'] = tempTopUsersRating.index
recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
recommendation_df.head(10)

movies_df.loc[movies_df['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]











