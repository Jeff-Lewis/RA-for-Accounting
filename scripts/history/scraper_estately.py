import requests
from bs4 import BeautifulSoup

# Define the URL of the webpage to scrape
# url = 'https://www.estately.com/NY/New_York'
# url = 'https://www.estately.com/40.2229,-74.8722,41.0265,-73.2242'

# # Send a GET request to the webpage
# response = requests.get(url)

# # Parse the webpage content with BeautifulSoup
# soup = BeautifulSoup(response.text, 'html.parser')
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode, without a UI
options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
options.add_argument('--no-sandbox')  # Disable the sandbox for the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Setup the driver (make sure to specify the path to where your webdriver is installed)
driver.get('https://www.estately.com/NY/New_York')

# Allow time for the page to load
time.sleep(5)

# If you need to scroll to trigger loading
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)  # Wait for the page to load more results

# If the site has a 'Next' button and you know you have multiple pages
while True:
    try:
        next_button = driver.find_element_by_xpath('//a[@rel="next"]')  # Adjust the XPath to match the 'Next' button
        next_button.click()
        time.sleep(5)  # Wait for new page of results to load
    except Exception as e:
        print("No more pages. Stopping.")
        break

# Now, you can scrape the loaded page
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')


# Initialize a list to hold all property data
properties = []

# Find all divs that represent a property listing
property_divs = soup.find_all('div', class_='result-item-info clearfix')

for div in property_divs:
    # Find the location within the <a> tag inside the <h2>
    location_tag = div.find('h2', class_='result-address').find('a')
    location = location_tag.text.strip() if location_tag else "No location provided"

    # Find the image URL in the img tag
    image_tag = div.find('img', class_='listing-card-image')
    # Check if 'data-src' exists, if not, fallback to 'src' or provide a default message
    image_url = image_tag.get('data-src', image_tag.get('src', "No image provided")) if image_tag else "No image provided"

    # Append the location and image URL to the properties list
    properties.append({'Location': location, 'Image URL': image_url})


# Output the data
print("Property Found:", len(properties))
# for property in properties:
#     print(property)

driver.quit()
