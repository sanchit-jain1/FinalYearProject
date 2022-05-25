# -*- coding: utf-8 -*-
"""finalYearProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WImuSJ7gKCXMn7KjHO1EAZdaCjHEJReA

Importing the Dependencies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import  train_test_split,cross_val_score,RandomizedSearchCV
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score


lr = LinearRegression()
rr = RandomForestRegressor()
gbr = GradientBoostingRegressor()
xgb = xgb.XGBRegressor()

import pickle


import warnings
warnings.filterwarnings('ignore')

"""Data Collections and Processing"""

# Loading Dataset from csv file
ds=pd.read_csv('dataset.csv')

#Inspecting first 5 rows in Dataset
ds.head()

#Getting information of dataset
ds.info()

ds.shape

ds.describe()

sns.heatmap(ds.isna(),annot=True)

# Drop null value because it is less then 5%
ds=ds.dropna()

#checking number of missing values
ds.isna().sum()

# checking the distribution of categorical data
print(ds.Fuel_Type.value_counts())
print(ds.Seller_Type.value_counts())
print(ds.Transmission.value_counts())
print(ds.Bs_version.value_counts())

"""#### there so many car name so we can not use car name to predict selling price becz there are many numbers of cars"""

final_dataset=ds[[ 'Year', 'Selling_Price', 'Present_Price', 'Kms_Driven',
       'Fuel_Type', 'Seller_Type', 'Transmission', 'Owner',"Bs_version"]]

final_dataset.head()

#Adding current year for predictions
final_dataset['Current_year']=2022
final_dataset.head()

"""#### To drive no_year to find selling price we used feature engneering to creat new column No_year using year and current_year column"""

final_dataset['No_years']=final_dataset['Current_year']-final_dataset['Year']
final_dataset.head()

"""# Droping year and Current_year  column becz now it off no use"""

final_dataset.drop(['Year','Current_year'],axis=1,inplace=True)
final_dataset.head()

# encoding "Fuel_Type" Column
final_dataset.replace({'Fuel_Type':{'Petrol':0,'Diesel':1,'CNG':2}},inplace=True)

# encoding "Seller_Type" Column
final_dataset.replace({'Seller_Type':{'Dealer':0,'Individual':1}},inplace=True)

# encoding "Transmission" Column
final_dataset.replace({'Transmission':{'Manual':0,'Automatic':1}},inplace=True)

# encoding "Bs_version" Column
final_dataset.replace({'Bs_version':{'bs3':0,'bs4':1}},inplace=True)

#printing new dataset in machine readable language
final_dataset.head()

"""## Correlation"""

final_dataset.corr()

plt.figure(figsize=(10,10))
sns.heatmap(final_dataset.corr(),annot=True)

sns.pairplot(final_dataset)

final_dataset['Selling_Price'].hist(bins=30)

"""#Divide x and y"""

X = final_dataset.drop(['Selling_Price'],axis=1)
Y = final_dataset['Selling_Price']

X

Y

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state=2)

"""#Show the important attributes in descending order"""

best_features = SelectKBest(score_func=f_regression, k='all')
top_features = best_features.fit(X_train,Y_train)
scores = pd.DataFrame(top_features.scores_)
columns = pd.DataFrame(X_train.columns)
featureScores = pd.concat([columns, scores], axis=1)
featureScores.columns = ['Features','Scores']
print(featureScores.nlargest(8, 'Scores'))

"""#Plot graph of feature importances for better visualization"""

featureScores.nlargest(8,'Scores').plot(kind='barh')
plt.show()

"""####Create function to displaying scores"""

def display_scores(scores):
    print("Scores: ", scores)
    print("Mean: ", scores.mean())
    print("Standard Deviation: ", scores.std())

"""#1.Training the Random Forest Regressor"""

print("Random Forest Regressor Scores")
scores = cross_val_score(rr, X_train, Y_train, scoring='neg_mean_squared_error', cv=5)
random_forest_scores = np.sqrt(-scores)
display_scores(random_forest_scores)
print("\n")

"""#2.Training the Gradient Boosting Regressor"""

print('Gradient Boosting Regressor Scores')
scores = cross_val_score(gbr, X_train, Y_train, scoring='neg_mean_squared_error', cv=5)
gradient_boosting_regressor = np.sqrt(-scores)
display_scores(gradient_boosting_regressor)
print("\n")

"""#3.Training the Linear Regression

"""

print('Linear Regression Scores')
scores = cross_val_score(lr, X_train, Y_train, scoring='neg_mean_squared_error', cv=5)
linear_regression = np.sqrt(-scores)
display_scores(linear_regression)
print("\n")

"""#4.Training the Extreme Gradient Boosting"""

print("xGB Scores")
scores = cross_val_score(xgb, X_train, Y_train, scoring='neg_mean_squared_error', cv=5)
xgb_regressor = np.sqrt(-scores)
display_scores(xgb_regressor)
print("\n")

"""#From our training model, Extreme Gradient Boosting has the best performance with the lower mean error. With this, we will used them for the prediction."""

xg_reg = XGBRegressor(objective ='reg:squarederror', colsample_bytree = 1, learning_rate = 0.15,
                max_depth = 5,n_estimators = 10)
xg_reg.fit(X_train,Y_train)

predictions= xg_reg.predict(X_test)
rmse = np.sqrt(mean_squared_error(Y_test,predictions))
print("RMSE: %f" % (rmse))

sns.distplot(Y_test-predictions)

plt.scatter(Y_test,predictions)

print('Accuracy:',r2_score(Y_test,predictions)*100)
print('Mean Absolute Error:', round(mean_absolute_error(Y_test, predictions),2))
print('Mean Squared Error:', round(mean_squared_error(Y_test, predictions),2))
print('Root Mean Squared Error:', round(np.sqrt(mean_squared_error(Y_test, predictions)),2))

predictions

# open a file, where you ant to store the data
file = open('xGBoost_model.pkl', 'wb')

# dump information to that file
pickle.dump(xg_reg, file)