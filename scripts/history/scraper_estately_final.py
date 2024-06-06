from construct import list_
from numpy import save
import requests
import os
import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def download_image(image_url, location, base_url='https://www.estately.com', save_dir='data/estately_images/queens'):
    if not image_url.startswith('http'):
        image_url = base_url + image_url
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = "".join([c for c in location if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    filename = filename.replace(' ', '_') + '.jpg'
    file_path = os.path.join(save_dir, filename)
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
        else:
            filename = None
    except requests.exceptions.RequestException:
        filename = None 
    return filename

def fetch_properties(driver, max_images=300, area = 'NY/New_York'):
    properties = []
    image_count = 0
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    property_divs = soup.find_all('div', class_='result-item-info clearfix')
    for div in property_divs:
        if image_count >= max_images:
            break
        location_tag = div.find('h2', class_='result-address').find('a')
        location = location_tag.text.strip() if location_tag else "No location provided"
        image_tag = div.find('img', class_='listing-card-image')
        detail_link = 'https://www.estately.com' + location_tag['href'] if location_tag else None

        # Price extraction
        price_tag = div.find('p', class_='result-price')
        price = price_tag.text.strip() if price_tag else "Price not listed"
        
        # Property type extraction
        property_type_tag = div.find('h2', class_='result-address').find('small')
        property_type = property_type_tag.text.strip() if property_type_tag else "Property type not listed"
        
        photo_count_tag = div.parent.find('div', class_='photo-count-small')
        photo_count = photo_count_tag.text.strip() if photo_count_tag else "No photo"
        
        broker_tag = div.parent.find('p')
        broker = broker_tag.text.strip() if broker_tag else "No broker listed"
        
        image_url = image_tag.get('data-src', image_tag.get('src', "No image provided")) if image_tag else "No image provided"
        image_name = download_image(image_url, location, save_dir=f'data/estately/img/{area}')
        
        # Basic details extraction
        basics_grid = div.find('ul', class_='result-basics-grid')
        beds = baths = sqft = lot_size = None 
        if basics_grid:
            for li in basics_grid.find_all('li'):
                text = li.text.strip()
                if 'bed' in text.lower():
                    beds = text.split()[0]
                elif 'bath' in text.lower():
                    baths = text.split()[0]
                elif 'sqft' in text.lower() and not 'lot' in text.lower():
                    sqft = text.split()[0]
                elif 'lot' in text.lower():
                    lot_size = text.split()[0]
        properties.append({
            'Location': location,
            'Detail Link': detail_link,
            'Image Name': image_name,
            'Price': price,
            'Property Type': property_type,
            'Photo Count': photo_count,
            'Broker': broker,
            'Beds': beds,
            'Baths': baths,
            'Sqft': sqft,
            'Lot Size': lot_size
        })
        image_count += 1
        if image_count % 20 == 0:
            print(f"Scraped {image_count} images.")
    return properties

def main(max_images=300, area = 'NY/New_York'):
    url = f'https://www.estately.com/{area}'
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    properties = fetch_properties(driver, max_images, area)
    driver.quit()
    df = pd.DataFrame(properties)
    return df

if __name__ == "__main__":
    # area = 'NY/Queens'
    # area = 'NY/Brooklyn'
    list_areas = ['NY/Queens', 'NY/Brooklyn', 'MD/Cumberland']
    area = list_areas[2]
    loc = area.replace('/', '_')
    df = main(300, area)
    print('='*50)
    print(f"Scraped {len(df)} properties in {area}.")
    print(df)
    print('='*50)
    df.to_csv(f'data/estately/property_data/{loc}', index=False) 
