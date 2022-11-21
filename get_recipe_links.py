import requests
from bs4 import BeautifulSoup
import time

RECIPE_SEARCH_URL = "https://cooking.nytimes.com/search?q=&page={page}"
RECIPE_LINK_FILE = "recipe_links.txt"

def main():
    page = 1
    recipe_links = []
    while page:
        page_contents = get_page_contents(page)
        time.sleep(10) 
        recipe_links.extend(get_recipe_links_on_page(page_contents))
        if on_last_page(page_contents):
            page = False
        else:
            page +=1

    with open(RECIPE_LINK_FILE, "w") as f:
        f.write("\n".join(recipe_links))

def get_page_contents(page):
    page_contents = requests.get(RECIPE_SEARCH_URL.format(page=page))
    return BeautifulSoup(page_contents.text, 'html.parser')

def get_recipe_links_on_page(page_contents):
    recipes = page_contents.find_all("a", class_="card-recipe-info")
    recipe_links = [recipe["href"] for recipe in recipes]
    return recipe_links

def on_last_page(page_contents):
    page_count = page_contents.find(id="pagination-count")
    if page_count:
        current_recipe_number, max_recipe_number = page_count.find_all("b")
        last_recipe_on_page = current_recipe_number.string.split()[-1]
        if last_recipe_on_page == max_recipe_number.string:
            return True
    return False

if __name__ == '__main__':
  main()