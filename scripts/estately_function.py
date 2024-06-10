# this is the template functions for the estately scraper
import numpy as np
import requests
import os
import time
import re
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import box
from tqdm import tqdm

# decorator
def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.2f} seconds to execute.")
        return result
    return wrapper

def read_non_empty_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return None
        return df
    except pd.errors.EmptyDataError:
        return None

# scraping functions
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
    options.add_argument("accept-language=en-US,en;q=0.9")
    options.add_argument("accept-encoding=gzip, deflate, br")
    options.add_argument("upgrade-insecure-requests=1")
    options.add_argument("cache-control=no-cache")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(options=options) # if error, use this version
    return driver

def download_image(image_url, location, geoid='10000000000', base_url='https://www.estately.com'):
    save_dir = os.path.join('results', geoid, 'images')
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

def fetch_on_sales_properties(driver, max_images=300, area = 'NY/New_York', geoid='10000000000'):
    properties = []
    image_count = 0
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    property_divs = soup.find_all('div', class_='result-item-info clearfix')
    print('properties found: ', len(property_divs))
    for div in property_divs:
#         if image_count >= max_images:
#             break
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
        image_name = None
        image_name = download_image(image_url, location, geoid)

        # Basic details extraction
        basics_grid = div.find('ul', class_='result-basics-grid')
        beds = baths = sqft = lot_size = days_on_site = None 
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
                elif 'on site' in text.lower():
                    days_on_site = text.split()[0]
        properties.append({
            'Location': location,
            'Detail Link': detail_link,
            'Image URL': image_url,
            'Image Name': image_name,
            'Price': price,
            'Property Type': property_type,
            'Photo Count': photo_count,
            'Broker': broker,
            'Beds': beds,
            'Baths': baths,
            'Sqft': sqft,
            'Lot Size': lot_size,
            'Days on Site': days_on_site
        })
        image_count += 1
        if image_count % 20 == 0:
            print(f"Scraped {image_count} images.")
    return properties

def fetch_sold_properties(driver, max_images=300, area = 'NY/New_York', geoid='10000000000'):
    properties = []
    image_count = 0
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    property_divs = soup.find_all('div', class_='result-item-info clearfix')
    print('properties found: ', len(property_divs))
    if len(property_divs) == 200:
        return properties, 200
    for div in property_divs:
#         if image_count >= max_images:
#             break
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
        image_name = None
        # image_name = download_image(image_url, location, geoid)

        sold_date_tag = div.find('small', string=re.compile(r'\d{1,2}/\d{1,2}/\d{2}'))
        sold_date = sold_date_tag.get_text(strip=True) if sold_date_tag else 'date not listed'

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
            'Lot Size': lot_size,
            'Sold Date': sold_date
        })
        image_count += 1
        if image_count % 50 == 0:
            print(f"Scraped {image_count} images.")
    return properties, len(property_divs)

def generate_grid_within_boundary(boundary, step=0.002):
    minx, miny, maxx, maxy = boundary.bounds
    grids = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            grid = box(x, y, x + step, y + step)
            if grid.intersects(boundary):
                grids.append(grid)
                # Plot the grid
                x1, y1, x2, y2 = grid.bounds
                plt.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], 'b-')
            y += step
        x += step
    print('>>>> total: ', len(grids), 'grids')
    
    plt.axis('equal')
    plt.show()
    return grids

@time_logger
def recursive_grid_scraping(miny, minx, maxy, maxx, step, geoid, scraping_type=None, driver=None):
    df_list = []
    main_call = lambda my, mx, my2, mx2: main(10000, f'{my},{mx},{my2},{mx2}', geoid, scraping_type, driver)

    def scrape_and_check_grid(my, mx, my2, mx2, current_step):
        my, mx, my2, mx2 = [round(val, 3) for val in [my, mx, my2, mx2]]
        df, count = main_call(my, mx, my2, mx2)
        if count >= 200 and current_step > 0.002:            
            new_step = current_step / 2
            print(f'breakdown steps to: {new_step}')
            grid_bounds = [
                (my, mx, (my + my2) / 2, (mx + mx2) / 2),
                (my, (mx + mx2) / 2, (my + my2) / 2, mx2),
                ((my + my2) / 2, mx, my2, (mx + mx2) / 2),
                ((my + my2) / 2, (mx + mx2) / 2, my2, mx2)
            ]
            for bounds in grid_bounds:
                df_list.extend(scrape_and_check_grid(*bounds, new_step))
        else:
            df_list.append(df)
        return df_list

    scrape_and_check_grid(miny, minx, maxy, maxx, step)
    return pd.concat(df_list)


def main_for_census_tract(tract_data, step, driver=None):
    
    # tqdm this
    for index, row in tqdm(tract_data.iterrows(), desc='>> Scraping tracts'):
        geoid = str(row['GEOID'])
        # results directory
        results_dir = os.path.join('results', geoid)
        cache_dir = os.path.join(results_dir, 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        print('='*50)
        print(f'>>> Scraping tract {geoid}, area: {round(row.to_dict()["area_sq_km"], 3)} sq km')
        boundary = row['geometry']
        grids = generate_grid_within_boundary(boundary, step)
        
        df_on_sales_list = []
        df_sold_list = []
        print('='*50)
        for i, grid in enumerate(tqdm(grids, desc=f">>> Scraping grids for tract {index} ")):
            minx, miny, maxx, maxy = [round(val, 3) for val in grid.bounds]
            
            print(f"Scraping grid: {miny},{minx},{maxy},{maxx}")
            # df_on_sales = recursive_grid_scraping(miny, minx, maxy, maxx, step, geoid, driver)
            # print('On sales Scrapped')
            df_sold = recursive_grid_scraping(miny, minx, maxy, maxx, step, geoid, 'sold', driver)
            print('Sold Scrapped')
            # df_on_sales_list.append(df_on_sales)
            df_sold_list.append(df_sold)
            
            
            on_sales_cache_path = os.path.join(cache_dir, f'df_on_sales_list_tract_{index}_part_{i}.csv')
            pd.concat(df_on_sales_list, ignore_index=True).to_csv(on_sales_cache_path, index=False)
            df_on_sales_list = []  # Clear the list after caching
            sold_cache_path = os.path.join(cache_dir, f'df_sold_list_tract_{index}_part_{i}.csv')
            pd.concat(df_sold_list, ignore_index=True).to_csv(sold_cache_path, index=False)
            df_sold_list = []  # Clear the list after caching
            print(f'>>>> tract {index} part {i} cached')
        if df_on_sales_list:
            on_sales_cache_path = os.path.join(cache_dir, f'df_on_sales_list_tract_{index}_part_{i//10 + 1}.csv')
            pd.concat(df_on_sales_list, ignore_index=True).to_csv(on_sales_cache_path, index=False)
            print(f'>>>> tract {index} part {i//10 + 1} cached')
        if df_sold_list:
            sold_cache_path = os.path.join(cache_dir, f'df_sold_list_tract_{index}_part_{i//10 + 1}.csv')
            pd.concat(df_sold_list, ignore_index=True).to_csv(sold_cache_path, index=False)
            print(f'>>>> tract {index} part {i//10 + 1} cached')
        # Combine cached files into final DataFrames
        on_sales_files = [f for f in os.listdir(cache_dir) if 'on_sales' in f]
        sold_files = [f for f in os.listdir(cache_dir) if 'sold' in f]
        
        if on_sales_files:
            on_sales_dfs = [read_non_empty_csv(os.path.join(cache_dir, f)) for f in on_sales_files]
            on_sales_dfs = [df for df in on_sales_dfs if df is not None]
            if on_sales_dfs:
                df_on_sales_combined = pd.concat(on_sales_dfs, ignore_index=True)
                on_sales_combined_path = os.path.join(results_dir, f'{geoid}_on_sales.csv')
                df_on_sales_combined.drop_duplicates().to_csv(on_sales_combined_path, index=False)
            else:
                print(f"No non-empty on-sales data for tract {geoid}")
        else:
            print(f"No on-sales data for tract {geoid}")

        if sold_files:
            sold_dfs = [read_non_empty_csv(os.path.join(cache_dir, f)) for f in sold_files]
            sold_dfs = [df for df in sold_dfs if df is not None]
            if sold_dfs:
                df_sold_combined = pd.concat(sold_dfs, ignore_index=True)
                sold_combined_path = os.path.join(results_dir, f'{geoid}_sold.csv')
                df_sold_combined.drop_duplicates().to_csv(sold_combined_path, index=False)
            else:
                print(f"No non-empty sold data for tract {geoid}")
        else:
            print(f"No sold data for tract {geoid}")
        
        # # Clean up cache directory
        # for f in os.listdir(cache_dir):
        #     os.remove(os.path.join(cache_dir, f))
        
        print(f"Finished scraping tract {index}.")

def main(max_images=300, area='NY/New_York', geoid='10000000000', scraping_type=None, driver=None):
    url = f'https://www.estately.com/{area}'
    if scraping_type and 'sold' in scraping_type:
        url += '?only_sold=sold'
    
    # print(area)
    if driver is None:
        driver = setup_driver()
    driver.get(url)
    time.sleep(5)
    
    if scraping_type and 'sold' in scraping_type:
        print(f'>>>> scraping {area}')
        properties, count = fetch_sold_properties(driver, max_images, area, geoid)

    else:
        properties = fetch_on_sales_properties(driver, max_images, area, geoid)
        count = 0
    
    driver.quit()
    df = pd.DataFrame(properties)
    return df, count


def download_images_and_update_csv(csv_file, geoid):
    df = pd.read_csv(csv_file)
    for idx, row in df.iterrows():
        image_url = row['Image URL']
        location = row['Location']
        if image_url and image_url != "No image provided":
            image_name = download_image(image_url, location, geoid)
            df.at[idx, 'Image Name'] = image_name
        else:
            df.at[idx, 'Image Name'] = "No image provided"
    
    df.drop_duplicates(inplace=True)  # Remove duplicates before saving
    df.to_csv(csv_file, index=False)
    print(f"Updated image names in {csv_file}")