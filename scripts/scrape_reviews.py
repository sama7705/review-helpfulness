import os
import re
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from robot import can_scrape


os.makedirs("../data", exist_ok=True)

all_reviews = []
review_id = 1


options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)


def safe_text(parent, selector):
    try:
        return parent.find_element(By.CSS_SELECTOR, selector).text.strip()
    except:
        return ""


steam_games = {
    "Dota 2": 570,
    "Counter Strike 2": 730,
    "Apex Legends": 1172470,
    "PUBG": 578080,
    "Team Fortress 2": 440,
    "Left 4 Dead 2": 550,
    "Warframe": 230410,
    "Stardew Valley": 413150
}


for game_name, app_id in steam_games.items():

    url = f"https://steamcommunity.com/app/{app_id}/reviews/?browsefilter=recent"

    if not can_scrape(url):
        print(game_name, "blocked by robots.txt")
        continue

    print(game_name, "allowed by robots.txt")

    driver.get(url)
    time.sleep(4)

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.apphub_Card")

    print(game_name, "Steam reviews found:", len(cards))

    for card in cards:

        review_text = safe_text(card, "div.apphub_CardTextContent")

        if len(review_text) < 20:
            continue

        review_title = safe_text(card, "div.title")
        review_date = safe_text(card, "div.date_posted")
        helpful_text = safe_text(card, "div.found_helpful")

        helpful_votes = 0

        match = re.search(
            r"(\d+)\s+people found this review helpful",
            helpful_text
        )

        if match:
            helpful_votes = int(match.group(1))

        rating = 0

        if "Not Recommended" in card.text:
            rating = 0
        elif "Recommended" in card.text:
            rating = 1

        total_votes = helpful_votes + 1
        helpfulness_score = helpful_votes / total_votes
        word_count = len(review_text.split())

        all_reviews.append({
            "review_id": review_id,
            "item_name": game_name,
            "review_title": review_title,
            "review_text": review_text,
            "rating": rating,
            "review_date": review_date,
            "helpful_votes": helpful_votes,
            "total_votes": total_votes,
            "helpfulness_score": helpfulness_score,
            "word_count": word_count,
            "helpful_label": 0,
            "source": "Steam",
            "review_url": url
        })

        review_id += 1


driver.quit()

df = pd.DataFrame(all_reviews)

if not df.empty:
    median_votes = df["helpful_votes"].median()

    df["helpful_label"] = df["helpful_votes"].apply(
        lambda x: 1 if x >= median_votes else 0
    )

df.to_csv("../data/raw_reviews.csv", index=False, encoding="utf-8-sig")

print("\nSaved: ../data/raw_reviews.csv")
print(df.shape)

if not df.empty:
    print(df["source"].value_counts())

    print("\nHelpful label distribution:")
    print(df["helpful_label"].value_counts())

    print("\nMedian helpful votes used as threshold:")
    print(median_votes)

    print("\nHelpful votes distribution:")
    print(df["helpful_votes"].describe())

    print("\nHelpful votes counts:")
    print(
        df["helpful_votes"]
        .value_counts()
        .sort_index()
        .head(20)
    )

else:
    print("No reviews scraped.")