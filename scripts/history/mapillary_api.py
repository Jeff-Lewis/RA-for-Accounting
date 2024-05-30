import requests
from geopy.geocoders import Nominatim

def geocode_address(address):
    """
    Converts address to latitude and longitude using the Nominatim geocoder.
    
    Args:
    - address (str): The address to geocode.
    
    Returns:
    - (float, float): A tuple containing latitude and longitude of the address.
    """
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return (None, None)

def find_nearby_images(latitude, longitude, access_token, radius=100, max_results=5):
    """
    Finds images close to a specified latitude and longitude using Mapillary API.
    
    Args:
    - latitude (float): Latitude of the location.
    - longitude (float): Longitude of the location.
    - access_token (str): Mapillary access token.
    - radius (int): Radius in meters to search within.
    - max_results (int): Maximum number of image results to return.
    
    Returns:
    - list: A list of dictionaries containing image IDs and URLs.
    """
    url = "https://graph.mapillary.com/images"
    params = {
        'access_token': access_token,
        'fields': 'id,thumb_1024_url,location',
        'closeto': f"{longitude},{latitude}",
        'radius': radius,
        'per_page': max_results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        images = response.json().get('data', [])
        print(f"Found {len(images)} images.")
        return [{'id': img['id'], 'url': img['thumb_1024_url'], 'location': img['location']} for img in images]
    else:
        print("Failed to fetch images:", response.status_code)
        return []

# Example usage
if __name__ == "__main__":
    address = "Brandenburg Gate, Berlin"  # Example address
    ACCESS_TOKEN = 'MLY|7527236837315710|51f7e3af1a75489feef95a94a886526c' 
    radius = 1500                         # Search within 150 meters
    max_results = 10                     # Get at most 10 results

    lat, lon = geocode_address(address)
    if lat and lon:
        print(f"Geocoded Coordinates: Latitude = {lat}, Longitude = {lon}")
        images = find_nearby_images(lat, lon, ACCESS_TOKEN, radius, max_results)
        for img in images:
            print(f"Image ID: {img['id']}, URL: {img['url']}, Location: {img['location']}")
    else:
        print("Failed to geocode address.")
