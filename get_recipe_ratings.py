import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

RECIPE_URL_BASE = "https://cooking.nytimes.com"
RECIPE_LINK_FILE = "recipe_links.txt"
RECIPE_METADATA_FILE = "recipe_metadata.csv"
AVG_RATING_REGEX = "avg_rating = .*;"
NUM_RATINGS_REGEX = "num_ratings = .*;"

def main():
    with open(RECIPE_LINK_FILE, "r") as f:
        recipe_links = f.read()
    recipe_links = recipe_links.split("\n")

    recipe_information = []
    for i, recipe_link in enumerate(recipe_links[649:]):
        if (i % 100) == 0:  # save intermediate progress
            pd.DataFrame.from_records(recipe_information).to_csv(RECIPE_METADATA_FILE, header=True, index=True)

        try:
            recipe_info = get_recipe_information(recipe_link)
        except:
            time.sleep(30)  # wait and retry if I've sent too many requests
            recipe_info = get_recipe_information(recipe_link)
        recipe_information.append(recipe_info)
        
    pd.DataFrame.from_records(recipe_information).to_csv(RECIPE_METADATA_FILE, header=True, index=True)

def get_recipe_information(recipe_link):
    page_contents = requests.get(f"{RECIPE_URL_BASE}{recipe_link}")
    soup = BeautifulSoup(page_contents.text, 'html.parser')
    recipe_title = soup.find("h1", class_="recipe-title").string.strip()
    rating_block = soup.find("script", string=re.compile("avg_rating"))
    return {"Recipe Title": recipe_title,
            "Average Rating": get_average_rating(rating_block),
            "Number of Ratings": get_num_ratings(rating_block),
            "Recipe Link": f"{RECIPE_URL_BASE}{recipe_link}"}

def get_average_rating(rating_block):
    if rating_block:
        return int(re.search(AVG_RATING_REGEX, rating_block.string)[0].strip(";").split()[-1])
    else:
        return 0

def get_num_ratings(rating_block):
    if rating_block:
        return int(re.search(NUM_RATINGS_REGEX, rating_block.string)[0].strip(";").split()[-1])
    else:
        return 0

if __name__ == '__main__':
  main()