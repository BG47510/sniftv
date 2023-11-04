#!/usr/bin/python3
# par github.com/BG47510
import requests
    
print("#EXTM3U")

pluto = "http://api.pluto.tv/v2/channels"
api = requests.get(pluto).json()

#m3u8 = api["stitched"]["urls"]["0"]["url"]

for p in api:
    print('')
    idflux = (f'{p["_id"]}') # aussi tvg-id
    url = (f'https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{idflux}/master.m3u8?\
deviceId=channel&deviceModel=web&deviceVersion=1.0&appVersion=1.0\
&deviceType=rokuChannel&deviceMake=rokuChannel&deviceDNT=1&advertisingId=channel\
&embedPartner=rokuChannel&appName=rokuchannel&is_lat=1&bmodel=bm1&content=channel\
&platform=web&tags=ROKU_CONTENT_TAGS&coppa=false&content_type=livefeed&rdid=channel\
&genre=ROKU_ADS_CONTENT_GENRE&content_rating=ROKU_ADS_CONTENT_RATING\
&studio_id=viacom&channel_id=channel')
    nom = (f',{p["name"]}')
    groupe = (f'#EXTINF:-1 group-title="{p["category"]}"')
    print(groupe + nom)
    print(url)
