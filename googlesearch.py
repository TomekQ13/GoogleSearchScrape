import requests
import os
from datetime import datetime
from pathlib import Path
from time import sleep
from utils import format_filename

imagesPath = Path('images/')

def makeGetRequest(googleQuery, searchImage = False, apiKey_environ='GOOGLE_API_KEY', cx_environ='GOOGLE_CSE', start=1, count=10):
    """
    Makes a request to googleapis. Uses environmental variables to get value for CSE and API key.
    Can perform  image or standard searches.
    Arguments:
    googleQuery - search query
    searchImage - boolean if images should be searched
    apiKey_environ - name of the env variable with the API key
    cx_environ - name of the Google Custom Search Engine identifier env variable
    start - the search result to start in the items array in the response e.g. 11 start at the first of the second page
    count - how many results per page - 1 - 10 inclusive, default 10
    Returns json.
    """
    params = {
        'key': os.environ.get('GOOGLE_API_KEY'),
        'cx': os.environ.get('GOOGLE_CSE'),
        'q': googleQuery,
        'count': count,
        'start': start
    }    
    if searchImage:
        params['searchType'] = 'image'

    return requests.get('https://www.googleapis.com/customsearch/v1', params=params).json()

def saveImage(imageURL, filename):
    """
    Makes a request to an URL containing an IMG and saves the image.
    Take imageURL as input, filename together with path as input and path.
    """
    try:
        r = requests.get(imageURL, stream=True)
    except:
        print("Request to the image URL failed. Skipping the image.")
        return

    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def iterItems(json_response):
    """
    Takes json response body from google api and results_func as an arguments and iterates over results.
    results_func must be a function which can be called in for item in items loop. It has to take one item of results as an argument.
    """
    items = json_response['items']
    for item in items:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        title = item['title']
        filename = format_filename(f'{timestamp}_{title}.jpg')
        saveImage(item['link'], imagesPath / filename)


def iterPages(googleQuery, pagesToScrape, searchImage=True, startPage=1, log=True, sleepSeconds=0):
    for i in range(pagesToScrape+startPage-1):
        r = makeGetRequest(googleQuery, searchImage=searchImage, start=startPage+10*i)
        iterItems(r)
        print(f'Finished scraping page {i+1}. Sleeping {sleepSeconds} seconds.' )
        sleep(sleepSeconds)

iterPages('cat', pagesToScrape=10, startPage=1, sleepSeconds=0)




