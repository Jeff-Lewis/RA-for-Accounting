import requests

def get_image_data(image_id, access_token):
    """
    Fetches metadata for a specific image from Mapillary.
    
    Args:
    - image_id (str): The Mapillary ID of the image to fetch.
    - access_token (str): Your Mapillary access token.
    
    Returns:
    - dict: A dictionary containing the image metadata.
    """
    url = f"https://graph.mapillary.com/{image_id}"
    params = {
        'access_token': access_token,
        'fields': 'id,thumb_256_url'
        # ,detections.value'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Returns the json response containing the image data
    else:
        return {'error': f"Failed to fetch image data: {response.status_code}"}

def find_images_nearby(latitude, longitude, access_token, radius=500, max_results=5):
    """
    Finds images close to specified latitude and longitude using the Mapillary API.
    
    Args:
    - latitude (float): Latitude of the location.
    - longitude (float): Longitude of the location.
    - access_token (str): Your Mapillary access token.
    - radius (int): Radius in meters to search within.
    - max_results (int): Maximum number of image results to return.
    
    Returns:
    - dict: A dictionary containing nearby images data.
    """
    url = f"https://graph.mapillary.com/images"
    params = {
        'access_token': access_token,
        'fields': 'id,computed_geometry',
        'closeto': f"{longitude},{latitude}",
        'radius': radius,
        'per_page': max_results
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Returns the json response containing images data
    else:
        return {'error': f"Failed to fetch images: {response.status_code}"}


def find_images_in_bbox(access_token, bbox, fields, page_size=2):
    """
    Searches for images within a specified bounding box using the Mapillary API.
    
    Args:
    - access_token (str): Your Mapillary access token.
    - bbox (str): Bounding box coordinates in the format "minLon,minLat,maxLon,maxLat".
    - fields (str): Comma-separated string of fields to return for each image. Default is 'id'.
    - page_size (int): Number of results to return per page.
    
    Returns:
    - list: A list of dictionaries, each containing data about one image.
    """
    url = "https://graph.mapillary.com/images"
    params = {
        'access_token': access_token,
        'bbox': bbox,
        'fields': fields,
        'per_page': page_size
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        images = response.json().get('data', [])
        print(f"Found {len(images)} images.")
        return images
        # Filter images to include only those with a 'building' detection
        building_images = [
            img for img in images if any(
                det['value'] == 'construction--structure--building' for det in img.get('detections', {}).get('data', [])
            )
        ]
        return building_images
    else:
        print(f"Failed to fetch images: {response.status_code}, {response.text}")
        return []
    

IMAGE_ID = '169979785061521'  # Replace with the actual Image ID
ACCESS_TOKEN = 'MLY|7527236837315710|51f7e3af1a75489feef95a94a886526c'  # Replace with your actual access token
latitude = 52.5200  # Example latitude (Berlin)
longitude = 13.4050

# image_data = get_image_data(IMAGE_ID, ACCESS_TOKEN)
# print(image_data)   

# nearby_images = find_images_nearby(latitude, longitude, ACCESS_TOKEN)
# print(nearby_images)

BBOX = '12.967,55.597,12.970,55.600'  
# BBOX = '12.967,55.597,13.008,55.607'
images = find_images_in_bbox(ACCESS_TOKEN, BBOX, fields='id,thumb_1024_url,detections.value', page_size=1)
print("Found images:")
# print(images)
# for img in images[:5]:
#     print(get_image_data(img['id'], ACCESS_TOKEN))
