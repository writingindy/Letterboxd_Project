# Letterboxd Project Analyzing Movie Preferences

### 1. Components
- data scraping from Letterboxd website, fetching data using The Movie Database (TMDb) API, as well as script data from various websites
- exploratory data analysis (EDA) on user movie data
- topic modeling on movie scripts

### 2. Status
On major components:
- [x] Data scraping from Letterboxd website
- [x] Data scraping from TMDb API
- [ ] Script scraping from various websites
- [ ] EDA on user movie data
        - [x] Runtime histogram
        - [x] Summary statistics on ratings

        - [ ] Budget and Revenue EDA
        - [ ] Popularity EDA
        - [ ] Language distribution + analysis on imbalanced language classes
- [ ] Topic modeling on movie scripts

On minor improvements:
- [ ] Put all helper functions into separate Python script that is imported into Python notebook
- [ ] Supplement genre information using Letterboxd website when TMDb API fails
- [ ] Improve initialization of TMDb data array to reduce amount of if-else statements in data extraction code
- [ ] Better colors for graphs + titles + legends
- [ ] Rewrite genre counts using pandas built-in functions sort_values and reindex

### 3. Instructions
Some instructions for running the notebook:

1. Create a virtual environment using the following command in PowerShell
```
py -m venv directory_name
```
2. Initialise the virtual environment using the following command in PowerShell
```
directory_name\Scripts\Activate.ps1
```
3. Run the following command with your virtual environment active to install all required dependencies
```
py -m pip install -r requirements.txt
```
4. Check that the notebook's Python kernel is switched to the virtual environment Python kernel!


For dev work:

- Remember to run the following command in your virtual environment (it'll save installed packages used in dev work)
```
py -m pip freeze > requirements.txt
```