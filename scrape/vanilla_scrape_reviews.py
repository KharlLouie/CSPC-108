import re
import json
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_shopee_reviews(url):
    print("Extracting shop_id and item_id from URL...")
    match = re.search(r'i\.(\d+)\.(\d+)', url)
    if not match:
        print("Invalid URL format.")
        return
    
    shop_id, item_id = match[1], match[2]
    ratings_url = f"https://shopee.ph/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={{offset}}&shopid={shop_id}&type=0"
    
    print("Setting up Selenium WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in the background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print("Error initializing WebDriver:", e)
        return
    
    print("Opening product page in browser...")
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    print("Scrolling to load more reviews...")
    for _ in range(3):  
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
    
    print("Extracting reviews...")
    reviews = driver.find_elements(By.CLASS_NAME, "shopee-product-rating__content")
    review_texts = [review.text for review in reviews if review.text]

    # Save reviews to CSV
    df = pd.DataFrame({"Review": review_texts})
    df.to_csv("shopee_reviews.csv", index=False)
    print("Scraping complete. Reviews saved in 'shopee_reviews.csv'.")
    
    driver.quit()
    
    # API Scraping for more reviews
    offset = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    while True:
        api_url = ratings_url.format(offset=offset)
        print(f"Fetching API reviews with offset {offset}...")
        try:
            response = requests.get(api_url, headers=headers)
        except requests.exceptions.RequestException as e:
            print("Error fetching API:", e)
            break
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            break

        try:
            data = response.json()
        except json.JSONDecodeError:
            print("Error decoding JSON response.")
            break

        if 'data' not in data or 'ratings' not in data['data']:
            print("No ratings found.")
            break
        
        for i, rating in enumerate(data['data']['ratings'], 1):
            print(f"Username: {rating.get('author_username', 'N/A')}")
            print(f"Rating: {rating.get('rating_star', 'N/A')}")
            print(f"Comment: {rating.get('comment', 'No comment')}")
            print('-' * 100)
        
        if len(data['data']['ratings']) < 20:
            print("No more reviews to fetch.")
            break
        
        offset += 20

if __name__ == "__main__":
    print("Enter URL:", end= " ")
    url = input()
    print("\nStarting Shopee review scraper...\n")
    get_shopee_reviews(url)
    print("\nScraper finished execution.")
