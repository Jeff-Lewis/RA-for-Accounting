# web scraper to get the data from mls.com
import requests
from bs4 import BeautifulSoup
import json

# URL of the page to scrape
url = 'https://mls.foreclosure.com/listing/search.html?ci=austin&st=tx'

# Send an HTTP GET request to the URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(url, headers=headers)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Look for script tags since the data is embedded in a script as JSON
scripts = soup.find_all('script', type='application/ld+json')

# This will store each property's details
properties = []

for script in scripts:
    # The JSON data is inside a <script> tag, extract and parse it
    try:
        data = json.loads(script.string)
        properties.append({
            'street_address': data.get('streetAddress'),
            'locality': data.get('addressLocality'),
            'region': data.get('addressRegion'),
            'postal_code': data.get('postalCode'),
            'latitude': data.get('geo', {}).get('latitude'),
            'longitude': data.get('geo', {}).get('longitude'),
            'details_url': data.get('url'),
            # If more details like bedrooms are consistently formatted, add them here
        })
    except json.JSONDecodeError:
        # If JSON decoding fails, skip to the next script tag
        continue

# # Now, `properties` list will contain all the property details that could be extracted
# for property in properties:
#     print(property)

property = properties[0]
details_url = property['details_url']

response = requests.get(details_url, headers=headers)
# `print(response.text)` is displaying the raw HTML content of the response received after sending an
# HTTP GET request to the URL specified in the `details_url` variable. This can help you inspect the
# structure of the webpage and understand how the data is organized, which is useful for further
# parsing and extracting specific information from the webpage.
# print(response.text)
soup = BeautifulSoup(response.text, 'html.parser')
# Dictionary to hold the property information
property_info = {}

# Find all the 'li' elements with class 'lci'
info_items = soup.find_all('li', class_='lci')

for item in info_items:
    # The label is contained within a span with class 'attr-label'
    label_span = item.find('span', class_='attr-label')
    # The value is the text of a following 'a' tag, but it's behind a login
    value_a = item.find('a')
    
    # Extract the text from the span and 'a' tag
    label = label_span.get_text(strip=True) if label_span else None
    value = value_a.get_text(strip=True) if value_a else 'Details require login'

    # Add to the dictionary
    if label:
        property_info[label] = value

print(property_info)


image_urls = []

# Find all image tags and extract their 'src' attributes
for img_tag in soup.find_all('img'):
    img_url = img_tag.get('src')
    if img_url:  # Only add if the URL is not None
        image_urls.append(img_url)

# Now you have all image URLs in the image_urls list
for url in image_urls:
    print(url)