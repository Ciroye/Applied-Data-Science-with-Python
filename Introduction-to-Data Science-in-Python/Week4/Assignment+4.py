
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[73]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[74]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[75]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    df = pd.DataFrame([],columns=["State", "RegionName"])
    with open('university_towns.txt' , "r") as file:
        for line in file:
            if '[edit]' in line:
                state = line[:line.find('[')].strip()
                continue
            region = line.strip()
            if "(" in region:
                region = region[:(region.find('(') - 1)]
            df = df.append(pd.DataFrame([[state,region]],columns=["State", "RegionName"]),ignore_index=True)
    return df


# In[76]:

def get_recession_start():
    gdp_data = pd.read_excel('gdplev.xls')
    gdp_data = (gdp_data.drop(['Current-Dollar and "Real" Gross Domestic Product',
                               'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5'],axis=1).ix[7:])
    gdp_data = gdp_data.rename(columns={'Unnamed: 4': 'Quarter','Unnamed: 6': "GDP"}).set_index('Quarter')
    index = gdp_data.index.get_loc('2000q1')
    gdp_data = gdp_data[index:]
    for i in range(1, len(gdp_data) - 1):
        if(gdp_data.iloc[i]["GDP"] < gdp_data.iloc[i-1]["GDP"]) and (gdp_data.iloc[i+1]["GDP"] < gdp_data.iloc[i]["GDP"]):
            return gdp_data.iloc[i].name


# In[77]:

def get_recession_end():
    gdp_data = pd.read_excel('gdplev.xls')
    gdp_data = (gdp_data.drop(['Current-Dollar and "Real" Gross Domestic Product',
                               'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5'],axis=1).ix[7:])
    gdp_data = gdp_data.rename(columns={'Unnamed: 4': 'Quarter','Unnamed: 6': "GDP"}).set_index('Quarter')
    recession_start = get_recession_start()
    index = gdp_data.index.get_loc(recession_start)
    for i in range(index + 2,len(gdp_data)):
        if(gdp_data.iloc[i]["GDP"] > gdp_data.iloc[i-1]["GDP"]) and (gdp_data.iloc[i-1]["GDP"] > gdp_data.iloc[i-2]["GDP"]):
            return gdp_data.iloc[i].name


# In[78]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp_data = pd.read_excel('gdplev.xls')
    gdp_data = (gdp_data.drop(['Current-Dollar and "Real" Gross Domestic Product',
                               'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 5'],axis=1).ix[7:])
    gdp_data = gdp_data.rename(columns={'Unnamed: 4': 'Quarter','Unnamed: 6': "GDP"}).set_index('Quarter')
    recession_start = gdp_data.index.get_loc(get_recession_start())
    recession_end = gdp_data.index.get_loc(get_recession_end())
    gdp_data = gdp_data[recession_start:recession_end+1]
    recession_bottom = gdp_data[gdp_data["GDP"] == np.min(gdp_data["GDP"])].iloc[0].name
    return recession_bottom


# In[79]:

def get_quarter():
    years = list(range(2000,2017))
    quarters = ["q1","q2","q3","q4"]
    quarters_years = []
    for year in years:
        for quarter in quarters:
            quarters_years.append(str(year)+quarter)
    quarters_years.pop()
    return quarters_years

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    df.drop(['Metro','CountyName','RegionID','SizeRank'],axis=1,inplace=1)
    df['State'] = df['State'].map(states)
    df.set_index(['State','RegionName'],inplace=True)
    col = list(df.columns)
    col = col[0:45]
    df.drop(col,axis=1,inplace=1)
    quarter = [list(df.columns)[x:x+3] for x in range(0, len(list(df.columns)), 3)]
    
    # new columns
    column_names = new_col_names()
    for col,quarter in zip(column_names,quarter):
        df[col] = df[quarter].mean(axis=1)
        
    df = df[column_names]
    return df


# In[80]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    df = convert_housing_data_to_quarters().copy()
    df = df.loc[:,'2008q3':'2009q2']
    df = df.reset_index()
    def price_ratio(row):
        return (row['2008q3'] - row['2009q2'])/row['2008q3']
    
    df["up-down"] = df.apply(price_ratio,axis=1)
    uni_town = get_list_of_university_towns()['RegionName']
    uni_town = set(uni_town)

    def is_uni_town(row):
        #check if the town is a university towns or not.
        if row['RegionName'] in uni_town:
            return 1
        else:
            return 0
    df['Uni'] = df.apply(is_uni_town,axis=1)
    uni = df[df["Uni"] == 1].loc[:,"up-down"].dropna()
    no_uni = df[df["Uni"] == 0].loc[:,"up-down"].dropna()
    def best():
        if uni.mean() < no_uni.mean():
            return "university town"
        else:
            return "non-university town"
    p_value = list(ttest_ind(uni,no_uni))[1]      
    return (True,p_value,best())

