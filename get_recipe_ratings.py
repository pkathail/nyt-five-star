import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

RECIPE_URL_BASE = "https://cooking.nytimes.com"
RECIPE_LINK_FILE = "recipe_links.txt"
RECIPE_METADATA_FILE = "recipe_metadata.csv"
AVG_RATING_REGEX = "avg_rating = [0-9];"
AVG_RATING_REGEX_2 = "ratingValue\":[0-9],"
NUM_RATINGS_REGEX = "num_ratings = ([0-9]*);"
NUM_RATINGS_REGEX_2 = "ratingCount\":([0-9]*)}"

def main():
    with open(RECIPE_LINK_FILE, "r") as f:
        recipe_links = f.read()
    recipe_links = recipe_links.split("\n")

    if os.path.exists(RECIPE_METADATA_FILE):
        recipe_information = pd.read_csv(RECIPE_METADATA_FILE, index_col=0)
        recipe_information = recipe_information[recipe_information["Average Rating"] != 0]
    else:
        recipe_information = pd.DataFrame([], columns=["Recipe Title", "Average Rating", "Number of Ratings", "Recipe Link"])

    for i, recipe_link in enumerate(recipe_links):
        if (i % 100) == 0:  # save intermediate progress
            recipe_information.to_csv(RECIPE_METADATA_FILE, header=True, index=True)

        if recipe_link not in recipe_information["Recipe Link"].values:
            try:
                recipe_info = get_recipe_information(recipe_link)
                recipe_information = recipe_information.append(recipe_info, ignore_index=True)
            except Exception as e:
                print(e)
                print(recipe_link)
                # time.sleep(30)  # wait and retry if I've sent too many requests
                # recipe_info = get_recipe_information(recipe_link)
        
    recipe_information.to_csv(RECIPE_METADATA_FILE, header=True, index=True)

def get_recipe_information(recipe_link):
    page_contents = requests.get(f"{RECIPE_URL_BASE}{recipe_link}")
    soup = BeautifulSoup(page_contents.text, 'html.parser')
    rating_block = soup.find("script", string=re.compile("rating"))
    return {"Recipe Title": get_recipe_title(soup),
            "Average Rating": get_average_rating(rating_block),
            "Number of Ratings": get_num_ratings(rating_block),
            "Recipe Link": f"{RECIPE_URL_BASE}{recipe_link}"}


def get_recipe_title(page_contents):
    recipe_title = page_contents.find("h1", class_="recipe-title")
    if recipe_title is None:
        recipe_title = page_contents.find("h1")
    recipe_title = recipe_title.string.strip()
    return recipe_title

def get_average_rating(rating_block):
    if rating_block:
        try:
            return int(re.search(AVG_RATING_REGEX, rating_block.string)[0].strip(";").split()[-1])
        except:
            return int(re.search(AVG_RATING_REGEX_2, rating_block.string)[0].strip(",")[-1])
    else:
        return 0

def get_num_ratings(rating_block):
    if rating_block:
        try:
            return int(re.search(NUM_RATINGS_REGEX, rating_block.string)[0].strip(";").split()[-1])
        except:
            return int(re.search(NUM_RATINGS_REGEX_2, rating_block.string)[0].split(":")[1].strip("}"))
    else:
        return 0

if __name__ == '__main__':
  main()
