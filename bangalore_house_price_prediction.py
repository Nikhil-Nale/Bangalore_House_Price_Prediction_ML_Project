# -*- coding: utf-8 -*-
"""Bangalore_House_Price_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SPPOSraSNRJ-ln1vIBOxmDyDgnNEm6X6

###Bangalore House Price Prediction

**Description**

What are the things that a potential home buyer considers before purchasing a house? The location, the size of the property, vicinity to offices, schools, parks, restaurants, hospitals or the stereotypical white picket fence? What about the most important factor — the price?

Now with the lingering impact of demonetization, the enforcement of the Real Estate (Regulation and Development) Act (RERA), and the lack of trust in property developers in the city, housing units sold across India in 2017 dropped by 7 percent. In fact, the property prices in Bengaluru fell by almost 5 percent in the second half of 2017, said a study published by property consultancy Knight Frank. For example, for a potential homeowner, over 9,000 apartment projects and flats for sale are available in the range of ₹42-52 lakh, followed by over 7,100 apartments that are in the ₹52-62 lakh budget segment, says a report by property website Makaan. According to the study, there are over 5,000 projects in the ₹15-25 lakh budget segment followed by those in the ₹34-43 lakh budget category.

Buying a home, especially in a city like Bengaluru, is a tricky choice. While the major factors are usually the same for all metros, there are others to be considered for the Silicon Valley of India. With its help millennial crowd, vibrant culture, great climate and a slew of job opportunities, it is difficult to ascertain the price of a house in Bengaluru.

**Problem Statemtent**

By analyzing these Bangalore house data we will determine the approximate price for the houses.

**Data Description**

Columns:

    area_type
    availability
    location
    size
    society
    total_sqft
    bath
    balcony
    price

**Importing Liabraries**
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
import matplotlib 
matplotlib.rcParams["figure.figsize"] = (20,10)
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score

"""**Reading the Data from the CSV file**"""

df = pd.read_csv("Bengaluru_House_Data.csv")
df.head()

# Printing the shape of the dataframe
df.shape

"""**Exploratory Data Analysis (EDA)**"""

# Total number of columns in the dataset
df.columns

# Information about the dataset
df.info()

# To know more about the dataset
df.describe()

# Checking if there is some null values or not
df.isnull()

# Checking if there is some null values or not
df.isnull().sum()

# Performing Group by operation on Area Type
df.groupby("area_type")["area_type"].agg("count")

df.info()

df.head()

# Dropping less important features
df = df.drop(["area_type", "society","balcony", "availability"], axis = "columns")

df.shape

# Dropping null values
df = df.dropna()

df.isnull().sum()

df.shape

"""**Feature Engineering**"""

# Applying unique function on feature called Size
df["size"].unique()

"""From the above we can clearly see that Bedroom is represented with 2 different methods. One is BHK and the other one is Bedroom. So we are making a new column called BHK and we are discarding all the units (like BHK, Bedroom)."""

df['BHK'] = df["size"].apply(lambda x: int(x.split(" ")[0]))

df.head()

df.total_sqft.unique()

# Exploring total_sqft feature
def is_float(x):
    try:
        float(x)
    except:
        return False
    return True

df[~df["total_sqft"].apply(is_float)].head(10)

"""From the above we can see that total_sqft can be a range (say, 3090-5002). For such cases we can just take average of the minimum and maximum value in the range. There are other cases such as 34.46Sq. Meter which one can convert to square ft using unit conversion. So, we are going to just drop such corner cases to keep things simple."""

def convert_sqft_to_number(x):
    tokens = x.split("-")
    if len(tokens) == 2:
        return (float(tokens[0])+float(tokens[1]))/2
    try:
        return float(x)
    except:
        return None

df = df.copy()
df["total_sqft"] = df["total_sqft"].apply(convert_sqft_to_number)
df.head(10)

"""Here, we are adding a new feature called Price per Square Feet"""

df = df.copy()
df["price_per_sqft"] = df["price"]*100000/df["total_sqft"]
df.head()

"""Here, we are going to use Dimentionality Reduction for the data which are categorical variable. We need to apply Dimensionality Reduction here to reduce number of locations.


"""

df.location = df.location.apply(lambda x: x.strip())       # strip()--that returns a copy of the string with both leading and trailing characters removed
location_stats = df['location'].value_counts(ascending=False)
location_stats

len(location_stats[location_stats<=10])

location_stats_less_than_10 = location_stats[location_stats<=10]
location_stats_less_than_10

df.location = df.location.apply(lambda x: 'other' if x in location_stats_less_than_10 else x)
len(df.location.unique())

df.head()

"""Here we will discard some more data. Because, normally if a square ft per bedroom is 300 (i.e. 2 bhk apartment is minimum 600 sqft. If you have for example 400 sqft apartment with 2 bhk than that seems suspicious and can be removed as an outlier. We will remove such outliers by keeping our minimum thresold per bhk to be 300 sqft"""

df[df.total_sqft/df.BHK<300].head()

df = df[~(df.total_sqft/df.BHK<300)]
df.shape

df.describe()

"""Here we find that min price per sqft is 267 rs/sqft whereas max is 12000000, this shows a wide variation in property prices. We should remove outliers per location using mean and one Standard Deviation"""

def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft>(m-st)) & (subdf.price_per_sqft<=(m+st))]
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out
df = remove_pps_outliers(df)
df.shape

df.head()

"""**Data Vizualization**"""

df.head(20)

# Ploting the Scatter Chart for 2 BHK and 3 BHK properties
def plot_scatter_chart(df,location):
    bhk2 = df[(df.location==location) & (df.BHK==2)]
    bhk3 = df[(df.location==location) & (df.BHK==3)]
    matplotlib.rcParams['figure.figsize'] = (8,6)
    plt.scatter(bhk2.total_sqft,bhk2.price,color='blue',label='2 BHK', s=50)
    plt.scatter(bhk3.total_sqft,bhk3.price,marker='+', color='green',label='3 BHK', s=50)
    plt.xlabel("Total Square Feet Area")
    plt.ylabel("Price (Lakh Indian Rupees)")
    plt.title(location)
    plt.legend()
    
plot_scatter_chart(df,"1st Phase JP Nagar")

# Ploting the histogram for Price Per Square Feet vs Count
plt.hist(df.price_per_sqft,rwidth=0.8)
plt.xlabel("Price Per Square Feet")
plt.ylabel("Count")

# Ploting the histogram for Number of bathrooms vs Count
plt.hist(df.bath,rwidth=0.8)
plt.xlabel("Number of bathrooms")
plt.ylabel("Count")

df[df.bath>10]

"""It is unusual to have 2 more bathrooms than number of bedrooms in a home. So we are discarding that also."""

df[df.bath>df.BHK+2]

df.head()

df.shape

"""**Using One Hot Encoding for Location**"""

dummies = pd.get_dummies(df.location)
dummies.head(20)

"""**Concatinating both the dataframes together**"""

df = pd.concat([df,dummies.drop('other',axis='columns')],axis='columns')
df.head()

df = df.drop('location',axis='columns')
df.head()

X = df.drop(['price'],axis='columns')
X.head()

X = df.drop(['size'],axis='columns')
X.head()

y = df.price
y.head()

X = X.drop(['price_per_sqft'],axis='columns')
X.head()

X = X.drop(['price'],axis='columns')
X.head()

X.shape

y.shape

"""**Train-Test Split**"""

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=42)

lr_clf = LinearRegression()
lr_clf.fit(X_train,y_train)
lr_clf.score(X_test,y_test)

cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
cross_val_score(LinearRegression(), X, y, cv=cv)

"""Here we are using Grid Search CV for 3 different types of Regression models.




*   Linear Regression
*   Lasso Regression
*   Decision Tree Regression

**Model Building**
"""

def find_best_model_using_gridsearchcv(X,y):
    algos = {
        'linear_regression' : {
            'model': LinearRegression(),
            'params': {
                'normalize': [True, False]
            }
        },
        'lasso': {
            'model': Lasso(),
            'params': {
                'alpha': [1,2],
                'selection': ['random', 'cyclic']
            }
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': {
                'criterion' : ['mse','friedman_mse'],
                'splitter': ['best','random']
            }
        }
    }
    scores = []
    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    for algo_name, config in algos.items():
        gs =  GridSearchCV(config['model'], config['params'], cv=cv, return_train_score=False)
        gs.fit(X,y)
        scores.append({
            'model': algo_name,
            'best_score': gs.best_score_,
            'best_params': gs.best_params_
        })

    return pd.DataFrame(scores,columns=['model','best_score','best_params'])

"""**Model Evaluation**"""

find_best_model_using_gridsearchcv(X,y)

"""**Model Testing**"""

def predict_price(location,sqft,bath,bhk):    
    loc_index = np.where(X.columns==location)[0][0]

    x = np.zeros(len(X.columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >= 0:
        x[loc_index] = 1

    return lr_clf.predict([x])[0]

"""Here we are predicting the house prices based on Location, Size, Bathroom, and BHK"""

predict_price('1st Phase JP Nagar',1000, 2, 2)

df.head()

predict_price('Banashankari Stage V',2000, 3, 3)

predict_price('2nd Stage Nagarbhavi',5000, 2, 2)

predict_price('Indira Nagar',1500, 3, 3)

"""### Conclusion

**From all the above models, we can clearly say that Linear Regression perform best for this dataset.**
"""

