# -*- coding: utf-8 -*-
"""Leaked_Data_Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dQ5qEttgeLw6oI_-IUGIt3MkRL5R_bCX

# Performing Exploratory Data Analysis on the Data
"""

# Commented out IPython magic to ensure Python compatibility.
# Required Libraries

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import warnings

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.compose import ColumnTransformer

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from sklearn.tree import export_graphviz
import pydot

import xgboost as xgb
from xgboost import plot_tree

import re

warnings.filterwarnings('ignore')
# %matplotlib inline

"""## Basic Data Inspection"""

# Checking the structure and Contents of the Dataset

LeakedData = pd.read_csv('Dataset.csv')
LeakedData.head()

# 1. Check for the Shape of the Dataframe

LeakedData.shape

# 2. Check for Null Values

nullVal = LeakedData.isnull().sum()

nullVal

# 3. Check for Data Types

dataTypes = LeakedData.dtypes

dataTypes



# 4. Checking Number of Values for Each Method

LeakedData['Method'].value_counts()

# 5. Get Summary Statistics on the Data

sumStats = LeakedData.describe(include='all')

sumStats

"""# Data Preprocessing"""

# 1. Handling Missing Values

cleanData = LeakedData.dropna(subset=['Records', 'Method', 'Sources'])

# Check for Null Values

null_values = cleanData.isnull().sum()
null_values

# Drop Nan rows in 'Year'

cleanData = cleanData.dropna(subset=['Year'])

# 2. Convert 'Year' to Numeric Data Format

cleanData['Year'] = pd.to_datetime(cleanData['Year'], errors = 'coerce').dt.year

cleanData['Year'].dtype

# Function to Handle Unwanted Records

def removeUnwantedData(cleanData):

  unwantedData = ['unknown', 'g20 world leaders', '19 years of data', '63 stores',
        'tens of thousands', 'over 5,000,000', 'unknown (client list)', 'millions',
        '235 gb', '350 clients emails', 'nan', '2.5gb', '250 locations',
        '500 locations', '10 locations', '93 stores', 'undisclosed',
        'source code compromised', '100 terabytes', '54 locations', '200 stores',
        '8 locations', '51 locations', 'tbc']
  cleanData['Records'] = cleanData['Records'].str.lower()
  cleanData = cleanData[~cleanData['Records'].isin(unwantedData)]

  if 'Unnamed: 0' in cleanData.columns:
    cleanData.rename(columns = {'Unnamed: 0':'Id'}, inplace = True)
    cleanData.reset_index(drop=True, inplace= True)

  return cleanData

cleanData.columns

cleanData = removeUnwantedData(cleanData)

cleanData.head()

cleanData = cleanData.drop(['Sources'], axis=1)

"""# Splitting into Training and Testing Sets"""

'''# Use Label Encoders to Handle Categorical Data
labelEncoders = {}

ColumnsToEncode = ['Entity', 'Organization type', 'Method']

for col in ColumnsToEncode:
  le = LabelEncoder()
  cleanData[col] = le.fit_transform(cleanData[col])
  labelEncoders[col] =  '''

categorical_columns = ['Entity', 'Organization type', 'Method']
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(), categorical_columns)
    ], remainder='passthrough')

X = preprocessor.fit_transform(cleanData)
y = cleanData['Records'].values

# Split Data (X, y)
X = cleanData.drop(['Id', 'Records', 'Sources'], axis=1)
y = cleanData['Records']

# Ensure y is fully numeric
y = pd.to_numeric(y, errors='coerce')

# Drop rows with NaN values in the target variable
valid_indices = ~np.isnan(y)
X = X[valid_indices]
y = y[valid_indices]

# Split into Train and Test Sets

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)

# Check Features and Labels of Training Set

print('Shape of Training Features:', train_X.shape)
print('Shape of Training Labels:', train_y.shape)

# Check Features and Labels of Testing Set

print('Shape of Test Features:', test_X.shape)
print('Shape of Test Labels:', test_y.shape)

# Baseline Model
# Predicting the Mean Values of Training Records

meanVal = train_y.mean()
baselinePrediction = [meanVal for _ in range(len(test_y))]
baselineErrors = abs(baselinePrediction - test_y)
print("Average Baseline Error is:", round(np.mean(baselineErrors)))

# Implementation of Random Forest
class RandomForest:
    def __init__(self, n_estimators=1000):
        self.n_estimators = n_estimators

    def fit(self, train_X, train_y):
        self.model = RandomForestRegressor(n_estimators=self.n_estimators, random_state=42)
        self.model.fit(train_X, train_y)
        return self.model

    def predict(self, test_X):
        pred = self.model.predict(test_X)
        return pred

    def evaluate(self, test_X, test_y):
        pred = self.model.predict(test_X)
        self.errors = abs(pred - test_y)
        self.average_error = round(np.mean(self.errors), 2)
        return self.average_error

    def evaluate_mape(self, test_X, test_y):
      pred = self.model.predict(test_X)
      mape = np.mean(np.abs((test_y - pred) / test_y)) * 100
      return mape

    def evaluate_relative_accuracy(self, test_X, test_y, tolerance=0.1):
        pred = self.model.predict(test_X)
        within_tolerance = np.abs((pred - test_y) / test_y) <= tolerance
        accuracy = np.mean(within_tolerance) * 100
        return accuracy

# Create and fit the RandomForest model
rf_model1 = RandomForest(n_estimators=100)
rf_model1.fit(train_X, train_y)

# Predict the Test data Results
rf_predictions = rf_model1.predict(test_X)

# Evaluate using MAPE
rf_mape = rf_model1.evaluate_mape(test_X, test_y)
print(f"Random Forest MAPE: {rf_mape:.2f}%")

# Evaluate Relative Accuracy

rf_relative_accuracy = rf_model1.evaluate_relative_accuracy(test_X, test_y, tolerance=0.1)
print(f"Random Forest Relative Accuracy: {rf_relative_accuracy:.2f}%")

import matplotlib.pyplot as plt


# Plot the Points
plt.figure(figsize=(10, 6))

# Plotting the actual vs predicted values
plt.scatter(test_y, rf_predictions, color='blue', alpha=0.6, label='Predicted Values (Blue Dots)')
plt.plot([min(test_y), max(test_y)], [min(test_y), max(test_y)], color='red', linestyle='--', label='Ideal Prediction (Red Line)')

# Adding Labels
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Predicted vs. Actual Values')
plt.legend()
plt.show()

