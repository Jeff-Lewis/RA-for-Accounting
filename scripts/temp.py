# import requests

# def find_building_images(access_token, bbox, max_results=1):
#     """
#     Finds images tagged with 'building' within a specified bounding box.
    
#     Args:
#     - access_token (str): Your Mapillary access token.
#     - bbox (str): Bounding box coordinates in the format "minLon,minLat,maxLon,maxLat".
#     - max_results (int): Maximum number of image results to return.
    
#     Returns:
#     - list: A list of image IDs that have been tagged with 'building'.
#     """
#     url = "https://graph.mapillary.com/images"
#     params = {
#         'access_token': access_token,
#         'bbox': bbox,
#         'fields': 'id,detections.value',
#         'per_page': max_results
#     }
    
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         images = response.json().get('data', [])
#         return images
#         # Filter images to include only those with a 'building' detection
#         # building_images = [
#         #     img for img in images if any(
#         #         det['value'] == 'object--building--yes' for det in img.get('detections', {}).get('data', [])
#         #     )
#         # ]
#         # return building_images
#     else:
#         print(f"Failed to fetch images: {response.status_code}, {response.text}")
#         return []

# # Example usage
# if __name__ == "__main__":
#     ACCESS_TOKEN = 'MLY|7527236837315710|51f7e3af1a75489feef95a94a886526c'
#     BBOX = '12.967,55.597,13.008,55.607'  # Example bounding box
    
#     building_images = find_building_images(ACCESS_TOKEN, BBOX)
#     print("Building Images Found:")
#     for img in building_images:
#         print(img)

import pandas as pd

# Read the CSS file into a DataFrame
df = pd.read_csv('data/property_images/property_data.csv', sep=',')

# Add prefix to "Detail Link" column
df['Detail Link'] = 'https://www.estately.com' + df['Detail Link']

# Display the DataFrame
print(df)
# # Save the DataFrame to a new CSV filex
df.to_csv('data/property_images/property_data.csv', index=False)
