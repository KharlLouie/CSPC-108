import re
import json
import time
import requests
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Function to scrape Shopee reviews
def get_shopee_reviews(url, max_reviews=50):
    print("Extracting shop_id and item_id from URL...")
    match = re.search(r'i\.(\d+)\.(\d+)', url)
    if not match:
        print("Invalid URL format.")
        return []
    
    shop_id, item_id = match[1], match[2]
    ratings_url = f"https://shopee.ph/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={{offset}}&shopid={shop_id}&type=0"
    
    print("Setting up Selenium WebDriver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)
    
    print("Scrolling to load more reviews...")
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)
    
    print("Extracting reviews...")
    reviews = driver.find_elements(By.CLASS_NAME, "shopee-product-rating__content")
    review_texts = [review.text.strip() for review in reviews if review.text][:max_reviews]
    driver.quit()
    
    return review_texts

# Function to scrape Lazada reviews (Placeholder for now)
def get_lazada_reviews(url, max_reviews=50):
    print("Lazada scraping is not implemented yet.")
    return []

# Function to train and evaluate the model
def train_model(reviews, labels):
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(reviews, labels, test_size=0.2, random_state=42)
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_tfidf, y_train)
    
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.2f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    return model, vectorizer

# Main function
def main():
    platform = input("Which platform would you like to scrape? (Shopee/Lazada): ").strip().lower()
    url = input("Enter the product URL: ").strip()
    
    if platform == "shopee":
        reviews = get_shopee_reviews(url, max_reviews=50)
    elif platform == "lazada":
        reviews = get_lazada_reviews(url, max_reviews=50)
    else:
        print("Invalid platform.")
        return
    
    if not reviews:
        print("No reviews found or failed to scrape the page.")
        return
    
    labels = np.random.choice([0, 1], size=len(reviews))  # Randomly labeling for now
    model, vectorizer = train_model(reviews, labels)
    
    while True:
        review_text = input("Enter a review to classify (or type 'exit' to stop): ")
        if review_text.lower() == 'exit':
            break
        review_tfidf = vectorizer.transform([review_text])
        prediction = model.predict(review_tfidf)[0]
        print("The review is classified as:", "Positive" if prediction == 1 else "Negative")

if __name__ == "__main__":
    main()