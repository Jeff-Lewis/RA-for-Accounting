import requests
import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Define the URL of the webpage to scrape
url = 'https://www.estately.com/NY/New_York'
# url = 'https://www.estately.com/40.2229,-74.8722,41.0265,-73.2242'

# Send a GET request to the webpage
response = requests.get(url)

# Parse the webpage content with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')


properties = []

# Iterate through each property listing found in the HTML
for div in soup.find_all('div', class_='result-item-details'):
    property_dict = {}

    location_link_tag = div.find('h2', class_='result-address').find('a')
    if location_link_tag:
        property_dict['Location'] = location_link_tag.text.strip()
        property_dict['Detail Link'] = location_link_tag['href']

    # Extracting image URL
    image_tag = div.find('img', class_='listing-card-image')
    property_dict['Image URL'] = image_tag['data-src'] if image_tag and 'data-src' in image_tag.attrs else (image_tag['src'] if image_tag and 'src' in image_tag.attrs else "No image provided")

    # Extracting price
    price_tag = div.find('p', class_='result-price')
    property_dict['Price'] = price_tag.text.strip() if price_tag else "No price listed"

    # Extracting property type
    property_type_tag = div.find('h2', class_='result-address').find('small')
    property_dict['Property Type'] = property_type_tag.text.strip() if property_type_tag else "No property type listed"

    # Extracting basic details (beds, baths, sqft)
    basics = div.find('ul', class_='result-basics-grid')
    if basics:
        for li in basics.find_all('li'):
            key = ' '.join(li.text.split()[-1:])  # The last word is usually beds, baths, sqft
            value = li.b.text if li.b else li.text.split()[0]
            property_dict[key.capitalize()] = value

    # Extracting number of photos
    photo_count_tag = div.parent.find('div', class_='photo-count-small')
    if photo_count_tag:
        property_dict['Photo Count'] = photo_count_tag.text.strip()

    # Extracting realty or broker name
    broker_tag = div.parent.find('p')
    if broker_tag:
        property_dict['Brokerage'] = broker_tag.text.strip()

    properties.append(property_dict)

# Output example
for property in properties:
    print(property)
