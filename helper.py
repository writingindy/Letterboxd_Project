import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from scipy import stats
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import seaborn as sns

api_pathway = './data/api_key.txt'
api_key = open(api_pathway, "r").read()

# Need to rewrite this function to check for whether key exists when making a dictionary call
# Also it's possible for movies to not have IMDb entries
def extract_TMDb_data(data):
    # Propagate primary key of data as secondary key for generated dataset
    secondary_key = range(0, len(data['Letterboxd URI']))

    # We'll use the URI column to get the IMDb IDs for each movie
    URI_list = data["Letterboxd URI"]

    # Might be better to initialize these as NA to the right size, could avoid large chunks of repeated code
    # setting them to be NA if they're not present in API call
    TMDb_IDs = []

    genres_list = []
    runtime_list = []
    revenue_list = []
    budget_list = []
    vote_average_list = []
    vote_count_list = []
    popularity_list = []
 

    for URI in URI_list:

        page = requests.get(URI)

        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find(class_="col-17")
        sections = results.find_all("section", class_="section col-10 col-main")

        for element in sections:
            paragraphs = element.find_all("p", class_="text-link text-footer")
            for hyperlink in paragraphs:
                links = hyperlink.find_all("a", class_="micro-button track-event")
                TMDb_check = False
                for link in links:
                    if link.text == "TMDb":
                        TMDb_check = True
                        TMDb_link = link["href"]
                        ID = TMDb_link.replace('https://www.themoviedb.org', '')

                        # Changes to True if it's a movie
                        type_flag = False

                        if '/movie/' in ID:
                            type_flag = True
                            ID = ID.replace('/movie/', '')
                            TMDb_ID = ID.rstrip(ID[-1])
                            TMDb_IDs.append(TMDb_ID)
                            #print(TMDb_ID)
                        elif '/tv/' in ID:
                            ID = ID.replace('/tv/', '')
                            TMDb_ID = ID.rstrip(ID[-1])
                            TMDb_IDs.append(TMDb_ID)
                            #print(TMDb_ID)
                        else:
                            genres_list.append(pd.NA)
                            runtime_list.append(pd.NA)
                            revenue_list.append(pd.NA)
                            budget_list.append(pd.NA)
                            vote_average_list.append(pd.NA)
                            vote_count_list.append(pd.NA)
                            popularity_list.append(pd.NA)


                        
                        if type_flag == True:
                            url = "https://api.themoviedb.org/3/movie/" + TMDb_ID + "?api_key=" + api_key
                        else:
                            url = "https://api.themoviedb.org/3/tv/" + TMDb_ID + "?api_key=" + api_key

                        
                        response = requests.get(url).json()
                        # Need to implement a check that the keys are in response

                        """if 'title' in response:
                            print(response['title'])
                        elif 'original_title' in response:
                            print(response['original_title'])
                        elif 'name' in response:
                            print(response['name'])"""
                        
                        if 'genres' in response:
                            movie_genres = []
                            for items in response['genres']:
                                movie_genres.append(items['name'])
                            #print(movie_genres)
                            genres_list.append(movie_genres)
                        else:
                            # Should probably implement a scrape on the Letterboxd website to get genres as alternative
                            # since the website has genre information from URI
                            genres_list.append(pd.NA)

                        if 'runtime' in response:
                            runtime_list.append(response['runtime'])
                        else:
                            runtime_list.append(pd.NA)
                        if 'revenue' in response:
                            revenue_list.append(response['revenue'])
                        else:
                            revenue_list.append(pd.NA)
                        if 'budget' in response:
                            budget_list.append(response['budget'])
                        else:
                            budget_list.append(pd.NA)
                        if 'vote_average' in response:
                            vote_average_list.append(response['vote_average'])
                        else:
                            vote_average_list.append(pd.NA)
                        if 'vote_count' in response:
                            vote_count_list.append(response['vote_count'])
                        else:
                            vote_count_list.append(pd.NA)
                        if 'popularity' in response:
                            popularity_list.append(response['popularity'])
                        else:
                            popularity_list.append(pd.NA)

                if TMDb_check == False:
                    genres_list.append(pd.NA)
                    runtime_list.append(pd.NA)
                    revenue_list.append(pd.NA)
                    budget_list.append(pd.NA)
                    vote_average_list.append(pd.NA)
                    vote_count_list.append(pd.NA)
                    popularity_list.append(pd.NA)




    TMDb_data = [secondary_key, genres_list, runtime_list, revenue_list, budget_list, vote_average_list, vote_count_list,
                     popularity_list]

    TMDb_data = pd.DataFrame(TMDb_data).T

    column_change = ['Key', 'Genres', 'Runtime', 'Revenue', 'Budget', 'Vote Average', 'Vote Count', 'Popularity']
    column_change = dict(enumerate(column_change))
    TMDb_data = TMDb_data.rename(columns= column_change)

    data_table = pd.merge(data, TMDb_data, how="inner", on="Key")

    return data_table


def genre_indicator_matrix(data):
    genres_list = data["Genres"].to_numpy().flatten().tolist()
    null_check = data["Genres"].isnull().to_numpy().tolist()
    
    total_genre_list = []
    for i in range(len(genres_list)):
        if null_check[i]:
            total_genre_list.append("NA")
        else:
            genres = genres_list[i]
            for genre in genres:
                total_genre_list.append(genre)

    genre_categories = np.unique(total_genre_list)

    # Initialize a dataframe of all zeros
    n_rows = len(data["Genres"])
    n_cols = len(genre_categories)
    indicator_matrix = pd.DataFrame(np.zeros((n_rows, n_cols)), columns=genre_categories)

    for i in range(len(data["Genres"])):
        indicator_matrix.loc[i, data.at[i, "Genres"]] = 1

    return pd.DataFrame(indicator_matrix)


def preprocess_data(data):
    # Drop rows with NaN entries
    processed_data = data.dropna()

    # Converts Year column from float to int
    processed_data = processed_data.astype({'Year':'int'})

    # This adds a primary key to the data
    primary_key = range(0, len(processed_data['Letterboxd URI']))
    processed_data.insert(0, column='Key', value = primary_key)

    data_table = extract_TMDb_data(processed_data)

    # Convert Genres data to indicator matrix
    indicator_matrix = genre_indicator_matrix(data_table)
    data_table = pd.concat([data_table, indicator_matrix], axis = 1)

    # TODO: This sets the datatypes of the data_table
    # Key: int


    return data_table


def top_N_genres(data, treshold = 5):
    genres_list = data["Genres"].to_numpy().flatten().tolist()
    null_check = data["Genres"].isnull().to_numpy().tolist()
    
    total_genre_list = []
    for i in range(len(genres_list)):
        if null_check[i]:
            total_genre_list.append("NA")
        else:
            genres = genres_list[i]
            for genre in genres:
                total_genre_list.append(genre)

    genre_categories = np.unique(total_genre_list)
    counts = pd.DataFrame(np.zeros(len(genre_categories))).T
    counts = counts.rename(columns= dict(enumerate(genre_categories)))

    # Rewrite this section to use count_values and reindex
    for genre in total_genre_list:
        for category in genre_categories:
            if genre == category:
                counts[category] += 1

    counts_column = dict(enumerate(["Counts"]))
    counts = counts.T
    counts = counts.rename(columns=counts_column)

    counts = counts.sort_values(by = ['Counts'], ascending=False)

    return counts.head(treshold)

# Summary statistics on ratings
# Ratings is an opinion variable, and thus we consider it an ordinal variable
def ratings_statistics(data):
    # Median of ratings
    print("Median of ratings is", data["Rating"].median())

    # 25th and 75th quantiles (equivalent to percentiles)
    print("The 25th and 75th percentiles of ratings are: \n", data["Rating"].quantile(q=[0.25, 0.75]))

    # Minimum rating is 0.5, maximum rating is 5.0
    row_index = np.arange(0.5, 5.5, 0.5)
    print(data["Rating"].value_counts(sort=False, dropna=False).reindex(row_index))
    data["Rating"].value_counts(sort=False, dropna=False).reindex(row_index).plot.bar()

    # Investigate movies rated 0.5 and 5.0!
    print("Bad Movies!")
    print(data[data["Rating"] == 0.5]["Name"].tolist())
    print("\n")
    print("Good Movies!")
    print(data[data["Rating"] == 5.0]["Name"].tolist())

# general histogram generator based on Freedman-Diaconis rule
def generate_histogram(data, feature):
    # We calculate the Freedman-Diaconis rule to obtain number of bins for histogram
    # count() and quartile() methods exclude NaN
    n_samples = data[feature].count()
    quartiles = data[feature].quantile([0.25, 0.75])
    h = 2*(quartiles[0.75] - quartiles[0.25])/(n_samples ** (1/3))
    num_bins = int((data[feature].max() - data[feature].min())/h)

    data[feature].hist(bins=num_bins, grid=False)

