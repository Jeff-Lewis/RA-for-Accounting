import os

import pytest

from streetview import search_panoramas

panos = search_panoramas(lat=41.8982208, lon=12.4764804)
first = panos[0]

print(first)
# pano_id='_R1mwpMkiqa2p0zp48EBJg' lat=41.89820676786453 lon=12.47644220919742 heading=0.8815613985061646 pitch=89.001953125 roll=0.1744659692049026 date='2019-08'
from streetview import get_panorama_meta

meta = get_panorama_meta(pano_id='_R1mwpMkiqa2p0zp48EBJg', api_key=GOOGLE_MAPS_API_KEY)

print(meta)
# date='2019-08' location=Location(lat=41.89820659475458, lng=12.47644649615282) pano_id='_R1mwpMkiqa2p0zp48EBJg'