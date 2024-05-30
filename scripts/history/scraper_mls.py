import requests
from bs4 import BeautifulSoup
import json

# Define the base URL for relative links
base_url = 'https://mls.foreclosure.com'

# URL of the page to scrape
search_url = 'https://mls.foreclosure.com/listing/search.html?ci=austin&st=tx'

# Send an HTTP GET request to the URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get(search_url, headers=headers)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# Look for script tags since the data is embedded in a script as JSON
scripts = soup.find_all('script', type='application/ld+json')

# This will store each property's basic details
properties = []

# Extract basic details from JSON data
for script in scripts:
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
        })
    except json.JSONDecodeError:
        continue

# Iterate over each property to get detailed information
for property in properties:
    details_url = property['details_url']
    if not details_url.startswith('http'):
        details_url = base_url + details_url  # Make sure the URL is complete
    
    response = requests.get(details_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Dictionary to hold the property information
    property_info = {}
    
    # Find all the 'li' elements with class 'lci' for detailed info
    info_items = soup.find_all('li', class_='lci')
    for item in info_items:
        label_span = item.find('span', class_='attr-label')
        value_a = item.find('a')
        label = label_span.get_text(strip=True) if label_span else None
        value = value_a.get_text(strip=True) if value_a else 'Details require login'
        if label:
            property_info[label] = value

    # Add the detailed info to the property's data
    property.update(property_info)


for property in properties:
    if 'Day(s) On Site:' not in property:
        continue
    for key, value in property.items():
        if value == None:
            continue
        print(f'{key}: {value}')
